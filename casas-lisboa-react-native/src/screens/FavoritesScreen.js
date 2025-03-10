import React from 'react';
import { View, Text, SafeAreaView } from 'react-native';
import Header from '../components/Header';

export default function FavoritesScreen() {
  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Header 
        title="Favorites" 
        showFilter={false}
      />
      <View className="flex-1 items-center justify-center p-4">
        <Text className="text-xl font-bold mb-2">Favorites</Text>
        <Text className="text-gray-500 text-center">Your favorite properties will appear here</Text>
      </View>
    </SafeAreaView>
  );
} 