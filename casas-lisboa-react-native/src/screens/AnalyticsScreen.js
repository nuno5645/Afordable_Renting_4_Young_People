import React from 'react';
import { View, Text, SafeAreaView } from 'react-native';
import Header from '../components/Header';

export default function AnalyticsScreen() {
  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Header 
        title="Analytics" 
        showFilter={false}
      />
      <View className="flex-1 items-center justify-center p-4">
        <Text className="text-xl font-bold mb-2">Analytics</Text>
        <Text className="text-gray-500 text-center">View statistics and trends about the rental market in Lisbon</Text>
      </View>
    </SafeAreaView>
  );
} 