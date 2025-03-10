import React from 'react';
import { View, Text, SafeAreaView, TextInput } from 'react-native';
import Ionicons from 'react-native-vector-icons/Ionicons';
import Header from '../components/Header';

export default function SearchScreen() {
  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Header 
        title="Search" 
        showFilter={false}
      />
      <View className="p-4">
        <View className="flex-row bg-gray-100 rounded-lg p-3 items-center mb-4">
          <Ionicons name="search-outline" size={20} color="#666" />
          <TextInput 
            placeholder="Search by location, price..."
            className="flex-1 ml-2"
          />
        </View>

        <View className="flex-1 items-center justify-center p-4">
          <Text className="text-xl font-bold mb-2">Find Properties</Text>
          <Text className="text-gray-500 text-center">Search for properties in Lisbon and surrounding areas</Text>
        </View>
      </View>
    </SafeAreaView>
  );
} 