import axios from 'axios';

// Simplified API URL - use proxy directly
const API_URL = '/api';

export interface House {
  name: string;
  zone: string;
  price: number;
  url: string;
  bedrooms: string;
  area: number;
  floor: string;
  description: string;
  freguesia: string;
  concelho: string;
  source: string;
  scraped_at: string;
  image_urls?: string[];
  contacted: boolean;
  discarded: boolean;
  favorite: boolean;
  house_id: string;
}

export interface ScraperStatus {
  name: string;
  status: string;
  timestamp: string;
  houses_processed: number;
  houses_found: number;
  error_message: string | null;
}

export interface ScraperStatusResponse {
  [key: string]: ScraperStatus;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

const api = {
  async getHouses(ordering?: string): Promise<House[]> {
    try {
      // Build URL string directly instead of using URL constructor
      let url = `${API_URL}/houses/`;
      if (ordering) {
        // Convert field names to lowercase for Django API
        const orderingField = ordering.startsWith('-') 
          ? '-' + ordering.substring(1).toLowerCase()
          : ordering.toLowerCase();
        url += `?ordering=${orderingField}`;
      }
      const response = await axios.get<PaginatedResponse<House>>(url);
      return response.data.results || [];
    } catch (error) {
      console.error('Error fetching houses:', error);
      return [];
    }
  },

  async toggleContacted(houseId: string): Promise<boolean> {
    try {
      const response = await axios.post(`${API_URL}/houses/${encodeURIComponent(houseId)}/toggle_contacted/`);
      return response.data.contacted;
    } catch (error) {
      console.error('Error toggling contacted status:', error);
      return false;
    }
  },

  async toggleDiscarded(houseId: string): Promise<boolean> {
    try {
      const response = await axios.post(`${API_URL}/houses/${encodeURIComponent(houseId)}/toggle_discarded/`);
      return response.data.discarded;
    } catch (error) {
      console.error('Error toggling discarded status:', error);
      return false;
    }
  },

  async toggleFavorite(houseId: string): Promise<boolean> {
    try {
      const response = await axios.post(`${API_URL}/houses/${encodeURIComponent(houseId)}/toggle_favorite/`);
      return response.data.favorite;
    } catch (error) {
      console.error('Error toggling favorite status:', error);
      return false;
    }
  },

  async getScraperStatus(): Promise<ScraperStatusResponse> {
    try {
      const response = await axios.get(`${API_URL}/scraper-status/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching scraper status:', error);
      return {};
    }
  }
};

export default api;