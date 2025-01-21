import axios from 'axios';

// Use relative URL which will be proxied through Vite
const API_URL = '/api';

export interface House {
  Name: string;
  Price: number;
  Area: number;
  Bedrooms: string;
  Location: string;
  URL: string;
  contacted: boolean;
  discarded: boolean;
  favorite: boolean;
}

const api = {
  async getHouses(sortColumn?: string, order: 'asc' | 'desc' = 'asc'): Promise<House[]> {
    try {
      console.log('Fetching from:', `${API_URL}/sort/${sortColumn || 'Price'}?order=${order}`);
      const response = await axios.get(`${API_URL}/sort/${sortColumn || 'Price'}?order=${order}`);
      return response.data.houses;
    } catch (error) {
      console.error('Error fetching houses:', error);
      return [];
    }
  },

  async toggleContacted(houseName: string): Promise<boolean> {
    try {
      const response = await axios.post(`${API_URL}/toggle-contacted/${encodeURIComponent(houseName)}`);
      return response.data.contacted;
    } catch (error) {
      console.error('Error toggling contacted status:', error);
      return false;
    }
  },

  async toggleDiscarded(houseName: string): Promise<boolean> {
    try {
      const response = await axios.post(`${API_URL}/toggle-discarded/${encodeURIComponent(houseName)}`);
      return response.data.discarded;
    } catch (error) {
      console.error('Error toggling discarded status:', error);
      return false;
    }
  },

  async toggleFavorite(houseName: string): Promise<boolean> {
    try {
      const response = await axios.post(`${API_URL}/toggle-favorite/${encodeURIComponent(houseName)}`);
      return response.data.favorite;
    } catch (error) {
      console.error('Error toggling favorite status:', error);
      return false;
    }
  }
};

export default api; 