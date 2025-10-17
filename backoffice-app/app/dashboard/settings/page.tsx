'use client';

import { useEffect, useState } from 'react';
import { authAPI, User } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import toast from 'react-hot-toast';
import { User as UserIcon, Mail, Phone, Settings as SettingsIcon } from 'lucide-react';

export default function SettingsPage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const data = await authAPI.getProfile();
      setUser(data);
    } catch (error: any) {
      toast.error('Failed to load profile');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading settings...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Failed to load user profile</div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 mt-1">Manage your account settings and preferences</p>
      </div>

      {/* Profile Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UserIcon className="w-5 h-5" />
            Profile Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Email</label>
            <div className="flex items-center gap-2">
              <Mail className="w-4 h-4 text-gray-400" />
              <Input value={user.email} disabled className="flex-1" />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Username</label>
            <div className="flex items-center gap-2">
              <UserIcon className="w-4 h-4 text-gray-400" />
              <Input value={user.username} disabled className="flex-1" />
            </div>
          </div>

          {user.profile.phone_number && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Phone Number</label>
              <div className="flex items-center gap-2">
                <Phone className="w-4 h-4 text-gray-400" />
                <Input value={user.profile.phone_number} disabled className="flex-1" />
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <SettingsIcon className="w-5 h-5" />
            Search Preferences
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Min Price</label>
              <Input
                type="number"
                value={user.profile.price_range_min || ''}
                disabled
                placeholder="No minimum"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Max Price</label>
              <Input
                type="number"
                value={user.profile.price_range_max || ''}
                disabled
                placeholder="No maximum"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Min Bedrooms</label>
              <Input
                type="number"
                value={user.profile.min_bedrooms || ''}
                disabled
                placeholder="Any"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Min Area (m²)</label>
              <Input
                type="number"
                value={user.profile.min_area || ''}
                disabled
                placeholder="Any"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={user.profile.notification_enabled}
              disabled
              className="rounded"
            />
            <label className="text-sm text-gray-700">Enable notifications</label>
          </div>
        </CardContent>
      </Card>

      {/* API Information */}
      <Card className="bg-gray-50">
        <CardContent className="pt-6">
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-gray-900">API Access</h3>
            <p className="text-sm text-gray-600">
              User ID: <code className="px-2 py-1 bg-white rounded border text-gray-900">{user.id}</code>
            </p>
            <p className="text-xs text-gray-500 mt-2">
              For API documentation, visit the Swagger UI at <code>/api/docs/</code>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
