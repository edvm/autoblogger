"""
Autoblogger - Generate content on demand using online data in real time.
Copyright (C) 2025  Emiliano Dalla Verde Marcozzi <edvm.inbox@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""App consumption endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from ..database import get_db, User, AppUsage
from ..auth import get_current_user
from .credits import consume_credits
from apps.blogger import get_blogger_app
from core.state import WorkflowState
from utils.filename import sanitize_filename_for_download

router = APIRouter()


# Pydantic models
class AppInfo(BaseModel):
    """App information model."""

    name: str
    description: str
    credits_required: int
    parameters: Dict[str, Any]


class BloggerAppRequest(BaseModel):
    """Blogger app request model."""

    topic: str
    search_depth: str = "basic"
    search_topic: str = "general"
    time_range: str = "month"
    days: int = 7
    max_results: int = 5
    include_domains: Optional[List[str]] = None
    exclude_domains: Optional[List[str]] = None
    include_answer: bool = False
    include_raw_content: bool = False
    include_images: bool = False
    timeout: int = 60


class AppUsageResponse(BaseModel):
    """App usage response model."""

    id: int
    app_name: str
    credits_consumed: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class BloggerAppResponse(BaseModel):
    """Blogger app response model."""

    usage_id: int
    status: str
    final_content: Optional[str] = None
    research_brief: Optional[Dict[str, Any]] = None
    sources: Optional[List[str]] = None
    error_message: Optional[str] = None


class UserContentItem(BaseModel):
    """User content item model."""

    id: int
    app_name: str
    topic: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    has_content: bool

    class Config:
        from_attributes = True


# Available apps configuration
AVAILABLE_APPS = {
    "blogger": AppInfo(
        name="blogger",
        description="AI-powered blog post generation with research, writing, and editing",
        credits_required=10,
        parameters={
            "topic": "string (required) - The topic for the blog post",
            "search_depth": "string (optional) - 'basic' or 'advanced'",
            "search_topic": "string (optional) - 'general', 'news', or 'finance'",
            "time_range": "string (optional) - 'day', 'week', 'month', or 'year'",
            "max_results": "integer (optional) - Maximum search results",
            "include_answer": "boolean (optional) - Include direct answers",
            "include_raw_content": "boolean (optional) - Include raw content",
            "include_images": "boolean (optional) - Include images",
        },
    )
}


@router.get("/usage/history", response_model=List[AppUsageResponse])
async def get_app_usage_history(
    limit: int = 50,
    offset: int = 0,
    app_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's app usage history."""
    query = db.query(AppUsage).filter(AppUsage.user_id == current_user.id)

    if app_name:
        query = query.filter(AppUsage.app_name == app_name)

    usages = (
        query.order_by(AppUsage.started_at.desc()).offset(offset).limit(limit).all()
    )

    return usages


@router.post("/blogger/generate", response_model=BloggerAppResponse)
async def generate_blog_post(
    request: BloggerAppRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a blog post using the blogger app."""

    app_info = AVAILABLE_APPS["blogger"]

    # Check if user has enough credits
    if current_user.credits < app_info.credits_required:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient credits. Required: {app_info.credits_required}, Available: {current_user.credits}",
        )

    # Create app usage record
    app_usage = AppUsage(
        user_id=current_user.id,
        app_name="blogger",
        credits_consumed=app_info.credits_required,
        status="pending",
        input_data=json.dumps(request.dict()),
    )

    db.add(app_usage)
    db.commit()
    db.refresh(app_usage)

    # Consume credits
    try:
        consume_credits(
            user=current_user,
            amount=app_info.credits_required,
            description=f"Blogger app usage: {request.topic}",
            reference_id=str(app_usage.id),
            db=db,
        )
    except HTTPException as e:
        # If credit consumption fails, mark usage as failed
        app_usage.status = "failed"
        app_usage.error_message = str(e.detail)
        app_usage.completed_at = datetime.utcnow()
        db.commit()
        raise e

    # Process the blog generation in background
    background_tasks.add_task(process_blogger_app, app_usage.id, request.dict())

    return BloggerAppResponse(usage_id=app_usage.id, status="pending")


@router.get("/blogger/usage/{usage_id}", response_model=BloggerAppResponse)
async def get_blogger_usage_status(
    usage_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the status and results of a blogger app usage."""

    usage = (
        db.query(AppUsage)
        .filter(
            AppUsage.id == usage_id,
            AppUsage.user_id == current_user.id,
            AppUsage.app_name == "blogger",
        )
        .first()
    )

    if not usage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usage not found"
        )

    response = BloggerAppResponse(
        usage_id=usage.id, status=usage.status, error_message=usage.error_message
    )

    if usage.output_data:
        try:
            output = json.loads(usage.output_data)
            response.final_content = output.get("final_content")
            response.research_brief = output.get("research_brief")
            response.sources = output.get("sources")
        except json.JSONDecodeError:
            pass

    return response


@router.get("/content", response_model=List[UserContentItem])
async def get_user_content(
    limit: int = 50,
    offset: int = 0,
    app_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's generated content from all apps."""
    query = db.query(AppUsage).filter(
        AppUsage.user_id == current_user.id, AppUsage.status == "completed"
    )

    if app_name:
        query = query.filter(AppUsage.app_name == app_name)

    usages = (
        query.order_by(AppUsage.completed_at.desc()).offset(offset).limit(limit).all()
    )

    content_items = []
    for usage in usages:
        # Extract topic from input_data
        topic = "Unknown topic"
        if usage.input_data:
            try:
                input_data = json.loads(usage.input_data)
                topic = input_data.get("topic", "Unknown topic")
            except json.JSONDecodeError:
                pass

        # Check if content exists
        has_content = False
        if usage.output_data:
            try:
                output_data = json.loads(usage.output_data)
                has_content = bool(output_data.get("final_content"))
            except json.JSONDecodeError:
                pass

        content_items.append(
            UserContentItem(
                id=usage.id,
                app_name=usage.app_name,
                topic=topic,
                status=usage.status,
                created_at=usage.started_at,
                completed_at=usage.completed_at,
                has_content=has_content,
            )
        )

    return content_items


@router.get("/content/{usage_id}/download")
async def download_content(
    usage_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download the generated content as a markdown file."""

    usage = (
        db.query(AppUsage)
        .filter(
            AppUsage.id == usage_id,
            AppUsage.user_id == current_user.id,
            AppUsage.status == "completed",
        )
        .first()
    )

    if not usage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found or not accessible",
        )

    if not usage.output_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No content available for download",
        )

    try:
        output_data = json.loads(usage.output_data)
        final_content = output_data.get("final_content")

        if not final_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No content available for download",
            )

        # Extract topic for filename
        topic = "generated_content"
        if usage.input_data:
            try:
                input_data = json.loads(usage.input_data)
                topic = input_data.get("topic", "generated_content")
            except json.JSONDecodeError:
                pass

        filename = sanitize_filename_for_download(topic, usage_id)

        return Response(
            content=final_content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid content format",
        )


@router.get("/", response_model=List[AppInfo])
async def list_available_apps():
    """List all available apps and their requirements."""
    return list(AVAILABLE_APPS.values())


@router.get("/{app_name}", response_model=AppInfo)
async def get_app_info(app_name: str):
    """Get information about a specific app."""
    if app_name not in AVAILABLE_APPS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"App '{app_name}' not found"
        )

    return AVAILABLE_APPS[app_name]


async def process_blogger_app(usage_id: int, request_data: dict):
    """Background task to process blogger app request."""
    from ..database import SessionLocal

    db = SessionLocal()
    try:
        usage = db.query(AppUsage).filter(AppUsage.id == usage_id).first()
        if not usage:
            return

        usage.status = "in_progress"
        db.commit()

        # Create blogger app with search options
        blogger_app = get_blogger_app(
            search_depth=request_data.get("search_depth", "basic"),
            topic=request_data.get("search_topic", "general"),
            time_range=request_data.get("time_range", "month"),
            days=request_data.get("days", 7),
            max_results=request_data.get("max_results", 5),
            include_domains=request_data.get("include_domains"),
            exclude_domains=request_data.get("exclude_domains"),
            include_answer=request_data.get("include_answer", False),
            include_raw_content=request_data.get("include_raw_content", False),
            include_images=request_data.get("include_images", False),
            timeout=request_data.get("timeout", 60),
        )

        # Create initial state
        initial_state = WorkflowState(initial_topic=request_data["topic"])

        # Generate blog post
        final_state = blogger_app.generate_blog_post(initial_state)

        # Save results
        output_data = {
            "final_content": final_state.final_content,
            "research_brief": final_state.research_brief,
            "sources": final_state.sources,
            "status": final_state.status,
        }

        usage.output_data = json.dumps(output_data)
        usage.status = "completed" if final_state.status == "COMPLETED" else "failed"
        usage.completed_at = datetime.utcnow()

        if final_state.status != "COMPLETED":
            usage.error_message = "Blog generation workflow failed"

        db.commit()

    except Exception as e:
        usage.status = "failed"
        usage.error_message = str(e)
        usage.completed_at = datetime.utcnow()
        db.commit()

    finally:
        db.close()
