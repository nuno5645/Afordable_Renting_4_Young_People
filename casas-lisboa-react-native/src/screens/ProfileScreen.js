import React from 'react';
import { View, Text, SafeAreaView, TouchableOpacity } from 'react-native';
import Ionicons from 'react-native-vector-icons/Ionicons';
import Header from '../components/Header';

export default function ProfileScreen() {
  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Header 
        title="Profile" 
        showFilter={false}
      />
      <View className="p-4">
        <View className="items-center justify-center py-6">
          <View className="h-24 w-24 bg-gray-300 rounded-full items-center justify-center mb-4">
            <Ionicons name="person" size={50} color="#666" />
          </View>
          <Text className="text-xl font-bold">User Profile</Text>
          <Text className="text-gray-500">user@example.com</Text>
        </View>
        
        <View className="bg-white rounded-lg mt-4 divide-y divide-gray-100">
          <TouchableOpacity className="flex-row items-center p-4">
            <Ionicons name="settings-outline" size={24} color="#666" className="mr-4" />
            <Text className="ml-3">Settings</Text>
          </TouchableOpacity>
          
          <TouchableOpacity className="flex-row items-center p-4">
            <Ionicons name="notifications-outline" size={24} color="#666" className="mr-4" />
            <Text className="ml-3">Notifications</Text>
          </TouchableOpacity>
          
          <TouchableOpacity className="flex-row items-center p-4">
            <Ionicons name="help-circle-outline" size={24} color="#666" className="mr-4" />
            <Text className="ml-3">Help & Support</Text>
          </TouchableOpacity>
          
          <TouchableOpacity className="flex-row items-center p-4">
            <Ionicons name="log-out-outline" size={24} color="#666" className="mr-4" />
            <Text className="ml-3">Logout</Text>
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
} 