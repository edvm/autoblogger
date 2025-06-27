const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://dev.orb.local:8000';

export interface User {
  id: number;
  clerk_user_id: string;
  email: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  credits: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreditBalance {
  user_id: number;
  credits: number;
  email: string;
}

export interface CreditTransaction {
  id: number;
  amount: number;
  transaction_type: string;
  description?: string;
  reference_id?: string;
  created_at: string;
}

export interface AppInfo {
  name: string;
  description: string;
  credits_required: number;
  parameters: Record<string, unknown>;
}

export interface AppUsage {
  id: number;
  app_name: string;
  credits_consumed: number;
  status: string;
  started_at: string;
  completed_at?: string;
  error_message?: string;
}

export interface BloggerRequest {
  topic: string;
  search_depth?: string;
  search_topic?: string;
  time_range?: string;
  days?: number;
  max_results?: number;
  include_domains?: string[];
  exclude_domains?: string[];
  include_answer?: boolean;
  include_raw_content?: boolean;
  include_images?: boolean;
  timeout?: number;
}

export interface BloggerResponse {
  usage_id: number;
  status: string;
  final_content?: string;
  research_brief?: Record<string, unknown>;
  sources?: string[];
  error_message?: string;
}

export interface UserContentItem {
  id: number;
  app_name: string;
  topic: string;
  status: string;
  created_at: string;
  completed_at?: string;
  has_content: boolean;
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  getToken?: () => Promise<string | null>
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (getToken) {
    const token = await getToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }
  
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      ...headers,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export function createApiClient(getToken: () => Promise<string | null>) {
  return {
    // User endpoints
    async getCurrentUser(): Promise<User> {
      return apiRequest<User>('/api/v1/users/me', {}, getToken);
    },

    async updateCurrentUser(data: {
      username?: string;
      first_name?: string;
      last_name?: string;
    }): Promise<User> {
      return apiRequest<User>('/api/v1/users/me', {
        method: 'PUT',
        body: JSON.stringify(data),
      }, getToken);
    },

    // Credits endpoints
    async getCreditBalance(): Promise<CreditBalance> {
      return apiRequest<CreditBalance>('/api/v1/credits/balance', {}, getToken);
    },

    async getCreditTransactions(
      limit: number = 50,
      offset: number = 0
    ): Promise<CreditTransaction[]> {
      return apiRequest<CreditTransaction[]>(
        `/api/v1/credits/transactions?limit=${limit}&offset=${offset}`,
        {},
        getToken
      );
    },

    async purchaseCredits(amount: number, paymentReference?: string): Promise<CreditTransaction> {
      return apiRequest<CreditTransaction>('/api/v1/credits/purchase', {
        method: 'POST',
        body: JSON.stringify({
          amount,
          payment_reference: paymentReference,
        }),
      }, getToken);
    },

    // Apps endpoints
    async getAvailableApps(): Promise<AppInfo[]> {
      return apiRequest<AppInfo[]>('/api/v1/apps/', {}, getToken);
    },

    async getAppInfo(appName: string): Promise<AppInfo> {
      return apiRequest<AppInfo>(`/api/v1/apps/${appName}`, {}, getToken);
    },

    async getAppUsageHistory(
      limit: number = 50,
      offset: number = 0,
      appName?: string
    ): Promise<AppUsage[]> {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
      });
      if (appName) {
        params.append('app_name', appName);
      }
      return apiRequest<AppUsage[]>(`/api/v1/apps/usage/history?${params}`, {}, getToken);
    },

    // Blogger app endpoints
    async generateBlogPost(request: BloggerRequest): Promise<BloggerResponse> {
      return apiRequest<BloggerResponse>('/api/v1/apps/blogger/generate', {
        method: 'POST',
        body: JSON.stringify(request),
      }, getToken);
    },

    async getBloggerUsageStatus(usageId: number): Promise<BloggerResponse> {
      return apiRequest<BloggerResponse>(`/api/v1/apps/blogger/usage/${usageId}`, {}, getToken);
    },

    // Content endpoints
    async getUserContent(
      limit: number = 50,
      offset: number = 0,
      appName?: string
    ): Promise<UserContentItem[]> {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
      });
      if (appName) {
        params.append('app_name', appName);
      }
      return apiRequest<UserContentItem[]>(`/api/v1/apps/content?${params}`, {}, getToken);
    },

    async downloadContent(usageId: number): Promise<Blob> {
      const headers: Record<string, string> = {};
      if (getToken) {
        const token = await getToken();
        if (token) {
          headers.Authorization = `Bearer ${token}`;
        }
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/apps/content/${usageId}/download`, {
        headers,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Download failed: ${response.status} ${errorText}`);
      }

      return response.blob();
    },
  };
}

