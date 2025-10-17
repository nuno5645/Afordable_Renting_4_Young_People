import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}/api/users/login/refresh/`, {
            refresh: refreshToken,
          });
          localStorage.setItem('access_token', data.access);
          originalRequest.headers.Authorization = `Bearer ${data.access}`;
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }
    return Promise.reject(error);
  }
);

export interface District {
  id: number;
  name: string;
}

export interface County {
  id: number;
  name: string;
  district: District;
}

export interface Parish {
  id: number;
  name: string;
  county: County;
}

export interface House {
  house_id: string;
  name: string;
  zone: string;
  price: string;
  url: string;
  bedrooms: string;
  area: string;
  floor: string | null;
  description: string;
  parish: Parish | null;
  county: County | null;
  district: District | null;
  source: string;
  scraped_at: string;
  is_favorite: boolean;
  is_contacted: boolean;
  is_discarded: boolean;
  photos: Photo[];
}

export interface Photo {
  image_url: string;
  order: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ScraperInfo {
  name: string;
  status: string | null;
  timestamp: string;
  houses_processed: number;
  houses_found: number;
  error_message: string | null;
}

export interface MainRunStatus {
  status: string | null;
  start_time: string | null;
  end_time: string | null;
  total_houses: number;
  new_houses: number;
  error_message: string | null;
  last_run_date: string | null;
}

export interface ScrapersStatusResponse {
  main_run: MainRunStatus;
  scrapers: Record<string, ScraperInfo>;
}

// Legacy interface for backward compatibility
export interface ScraperStatus {
  scraper_name: string;
  last_run: string;
  status: string;
  houses_found: number;
  errors: string[];
}

export interface User {
  id: number;
  email: string;
  username: string;
  profile: UserProfile;
}

export interface UserProfile {
  profile_picture: string | null;
  phone_number: string | null;
  preferred_zones: any;
  price_range_min: string | null;
  price_range_max: string | null;
  min_bedrooms: number | null;
  min_area: number | null;
  notification_enabled: boolean;
}

// API Functions
export const authAPI = {
  login: async (email: string, password: string) => {
    const { data } = await api.post('/api/users/login/', { email, password });
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    return data;
  },
  
  register: async (email: string, username: string, password: string, password2: string) => {
    const { data } = await api.post('/api/users/register/', { 
      email, 
      username, 
      password, 
      password2 
    });
    return data;
  },
  
  logout: async () => {
    try {
      await api.post('/api/users/logout/');
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },
  
  getProfile: async (): Promise<User> => {
    const { data } = await api.get('/api/users/profile/');
    return data;
  },
};

export interface HouseFilters {
  ordering?: string;
  page?: number;
  district?: number;
  county?: number;
  parish?: number;
  favorites?: boolean;
  contacted?: boolean;
}

export const housesAPI = {
  getAll: async (params?: HouseFilters): Promise<PaginatedResponse<House>> => {
    const { data } = await api.get('/api/houses/', { params });
    return data;
  },
  
  getById: async (id: string): Promise<House> => {
    const { data } = await api.get(`/api/houses/${id}/`);
    return data;
  },
  
  toggleFavorite: async (houseId: string): Promise<{ is_favorite: boolean }> => {
    const { data } = await api.post(`/api/houses/${houseId}/toggle_favorite/`);
    return data;
  },
  
  toggleContacted: async (id: string): Promise<{ is_contacted: boolean }> => {
    const { data } = await api.post(`/api/houses/${id}/toggle_contacted/`);
    return data;
  },
  
  toggleDiscarded: async (id: string): Promise<{ is_discarded: boolean }> => {
    const { data } = await api.post(`/api/houses/${id}/toggle_discarded/`);
    return data;
  },
  
  update: async (id: string, data: Partial<House>): Promise<House> => {
    const response = await api.patch(`/api/houses/${id}/`, data);
    return response.data;
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/houses/${id}/`);
  },
};

export interface RunScrapersRequest {
  scrapers?: string[];  // Optional: specific scrapers to run (e.g., ['ImoVirtual', 'Idealista'])
  all?: boolean;        // Optional: run all scrapers
}

export interface RunScrapersResponse {
  status: 'success' | 'error';
  output?: string;
  error?: string;
  scrapers_run?: string | string[];
  message?: string;
}

export const scrapersAPI = {
  getStatus: async (): Promise<ScrapersStatusResponse> => {
    const { data } = await api.get('/api/scraper-status/');
    return data;
  },
  
  runScrapers: async (request?: RunScrapersRequest): Promise<RunScrapersResponse> => {
    const { data } = await api.post('/api/run-scrapers/', request || {});
    return data;
  },
};

export const locationsAPI = {
  // Districts
  getDistricts: async (): Promise<District[]> => {
    const { data } = await api.get('/api/districts/', { params: { page_size: 1000 } });
    // Handle both paginated and non-paginated responses
    return data.results || data;
  },
  
  getDistrictById: async (id: number): Promise<District> => {
    const { data } = await api.get(`/api/districts/${id}/`);
    return data;
  },
  
  getDistrictCounties: async (id: number): Promise<County[]> => {
    const { data } = await api.get(`/api/districts/${id}/counties/`);
    // This endpoint returns an array directly, not paginated
    return data;
  },
  
  getDistrictHouses: async (id: number, page?: number): Promise<PaginatedResponse<House>> => {
    const { data } = await api.get(`/api/districts/${id}/houses/`, { params: { page } });
    return data;
  },
  
  // Counties
  getCounties: async (params?: { district?: number }): Promise<County[]> => {
    const { data } = await api.get('/api/counties/', { params: { ...params, page_size: 1000 } });
    // Handle both paginated and non-paginated responses
    return data.results || data;
  },
  
  getCountyById: async (id: number): Promise<County> => {
    const { data } = await api.get(`/api/counties/${id}/`);
    return data;
  },
  
  getCountyParishes: async (id: number): Promise<Parish[]> => {
    const { data } = await api.get(`/api/counties/${id}/parishes/`);
    // This endpoint returns an array directly, not paginated
    return data;
  },
  
  getCountyHouses: async (id: number, page?: number): Promise<PaginatedResponse<House>> => {
    const { data } = await api.get(`/api/counties/${id}/houses/`, { params: { page } });
    return data;
  },
  
  // Parishes
  getParishes: async (params?: { county?: number; district?: number }): Promise<Parish[]> => {
    const { data } = await api.get('/api/parishes/', { params: { ...params, page_size: 1000 } });
    // Handle both paginated and non-paginated responses
    return data.results || data;
  },
  
  getParishById: async (id: number): Promise<Parish> => {
    const { data } = await api.get(`/api/parishes/${id}/`);
    return data;
  },
  
  getParishHouses: async (id: number, page?: number): Promise<PaginatedResponse<House>> => {
    const { data } = await api.get(`/api/parishes/${id}/houses/`, { params: { page } });
    return data;
  },
};

export default api;
