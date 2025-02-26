import axios from 'axios';

// Use ngrok URL only in production, otherwise use local proxy
const API_URL = import.meta.env.VITE_APP_ENV === 'prod' 
  ? `${import.meta.env.VITE_NGROK_URL}/api`
  : '/api';

export interface House {
  Name: string;
  Zone: string;
  Price: number;
  URL: string;
  Bedrooms: string;
  Area: number;
  Floor: string;
  Description: string;
  Freguesia: string;
  Concelho: string;
  Source: string;
  'Scraped At': string;
  'Image URLs'?: string[];
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

const api = {
  async getHouses(): Promise<House[]> {
    try {
      const response = await axios.get(`${API_URL}/houses`);
      return response.data.houses;
    } catch (error) {
      console.error('Error fetching houses:', error);
      return [];
    }
  },

  async toggleContacted(houseId: string): Promise<boolean> {
    try {
      const response = await axios.post(`${API_URL}/toggle-contacted?house_id=${encodeURIComponent(houseId)}`);
      return response.data.contacted;
    } catch (error) {
      console.error('Error toggling contacted status:', error);
      return false;
    }
  },

  async toggleDiscarded(houseId: string): Promise<boolean> {
    try {
      const response = await axios.post(`${API_URL}/toggle-discarded?house_id=${encodeURIComponent(houseId)}`);
      return response.data.discarded;
    } catch (error) {
      console.error('Error toggling discarded status:', error);
      return false;
    }
  },

  async toggleFavorite(houseId: string): Promise<boolean> {
    try {
      const response = await axios.post(`${API_URL}/toggle-favorite?house_id=${encodeURIComponent(houseId)}`);
      return response.data.favorite;
    } catch (error) {
      console.error('Error toggling favorite status:', error);
      return false;
    }
  },

  async getScraperStatus(): Promise<ScraperStatusResponse> {
    try {
      const response = await axios.get(`${API_URL}/scraper-status`);
      return response.data;
    } catch (error) {
      console.error('Error fetching scraper status:', error);
      return {};
    }
  }
};

export default api;