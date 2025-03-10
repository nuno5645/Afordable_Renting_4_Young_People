import React, { useState } from 'react';
import { 
  View, 
  Text, 
  Modal, 
  TouchableOpacity, 
  TouchableWithoutFeedback,
  ScrollView,
  Switch
} from 'react-native';
import Ionicons from 'react-native-vector-icons/Ionicons';
import Slider from '@react-native-community/slider';

export default function FilterModal({ visible, onClose, onApply }) {
  const [minPrice, setMinPrice] = useState(500);
  const [maxPrice, setMaxPrice] = useState(2000);
  const [hasParking, setHasParking] = useState(false);
  const [filters, setFilters] = useState({
    bedrooms: 0,
    bathrooms: 0,
    furnished: false,
    pets: false
  });

  const handleApplyFilters = () => {
    // Construct filter object
    const appliedFilters = {
      priceRange: [minPrice, maxPrice],
      hasParking,
      ...filters
    };
    
    onApply(appliedFilters);
    onClose();
  };

  return (
    <Modal
      animationType="slide"
      transparent={true}
      visible={visible}
      onRequestClose={onClose}
    >
      <TouchableWithoutFeedback onPress={onClose}>
        <View className="flex-1 bg-black/50 justify-end">
          <TouchableWithoutFeedback onPress={() => {}}>
            <View className="bg-white rounded-t-3xl">
              {/* Header */}
              <View className="flex-row justify-between items-center p-4 border-b border-gray-200">
                <TouchableOpacity onPress={onClose}>
                  <Text className="text-gray-500">Cancel</Text>
                </TouchableOpacity>
                <Text className="text-lg font-bold">Filters</Text>
                <TouchableOpacity onPress={() => {
                  setMinPrice(500);
                  setMaxPrice(2000);
                  setHasParking(false);
                  setFilters({
                    bedrooms: 0,
                    bathrooms: 0,
                    furnished: false,
                    pets: false
                  });
                }}>
                  <Text className="text-blue-500">Reset</Text>
                </TouchableOpacity>
              </View>

              {/* Filter Content */}
              <ScrollView className="max-h-[500px]">
                {/* Price Range */}
                <View className="p-4 border-b border-gray-100">
                  <Text className="text-lg font-semibold mb-4">Price Range</Text>
                  <Text className="text-gray-700 mb-2">€{minPrice} - €{maxPrice}</Text>
                  <Slider
                    minimumValue={0}
                    maximumValue={5000}
                    minimumTrackTintColor="#3b82f6"
                    maximumTrackTintColor="#d1d5db"
                    step={50}
                    value={minPrice}
                    onValueChange={setMinPrice}
                  />
                  <Slider
                    minimumValue={0}
                    maximumValue={5000}
                    minimumTrackTintColor="#3b82f6"
                    maximumTrackTintColor="#d1d5db"
                    step={50}
                    value={maxPrice}
                    onValueChange={setMaxPrice}
                  />
                </View>

                {/* Rooms */}
                <View className="p-4 border-b border-gray-100">
                  <Text className="text-lg font-semibold mb-4">Rooms</Text>
                  
                  <View className="flex-row justify-between items-center mb-4">
                    <Text className="text-gray-700">Bedrooms</Text>
                    <View className="flex-row items-center">
                      <TouchableOpacity 
                        className="w-8 h-8 bg-gray-200 rounded-full items-center justify-center"
                        onPress={() => setFilters({...filters, bedrooms: Math.max(0, filters.bedrooms - 1)})}
                      >
                        <Ionicons name="remove" size={20} color="#666" />
                      </TouchableOpacity>
                      <Text className="mx-4 text-lg">{filters.bedrooms}</Text>
                      <TouchableOpacity 
                        className="w-8 h-8 bg-gray-200 rounded-full items-center justify-center"
                        onPress={() => setFilters({...filters, bedrooms: filters.bedrooms + 1})}
                      >
                        <Ionicons name="add" size={20} color="#666" />
                      </TouchableOpacity>
                    </View>
                  </View>
                  
                  <View className="flex-row justify-between items-center">
                    <Text className="text-gray-700">Bathrooms</Text>
                    <View className="flex-row items-center">
                      <TouchableOpacity 
                        className="w-8 h-8 bg-gray-200 rounded-full items-center justify-center"
                        onPress={() => setFilters({...filters, bathrooms: Math.max(0, filters.bathrooms - 1)})}
                      >
                        <Ionicons name="remove" size={20} color="#666" />
                      </TouchableOpacity>
                      <Text className="mx-4 text-lg">{filters.bathrooms}</Text>
                      <TouchableOpacity 
                        className="w-8 h-8 bg-gray-200 rounded-full items-center justify-center"
                        onPress={() => setFilters({...filters, bathrooms: filters.bathrooms + 1})}
                      >
                        <Ionicons name="add" size={20} color="#666" />
                      </TouchableOpacity>
                    </View>
                  </View>
                </View>

                {/* Features */}
                <View className="p-4 border-b border-gray-100">
                  <Text className="text-lg font-semibold mb-4">Features</Text>
                  
                  <View className="flex-row justify-between items-center mb-4">
                    <Text className="text-gray-700">Parking</Text>
                    <Switch
                      trackColor={{ false: "#d1d5db", true: "#bfdbfe" }}
                      thumbColor={hasParking ? "#3b82f6" : "#f4f3f4"}
                      value={hasParking}
                      onValueChange={setHasParking}
                    />
                  </View>
                  
                  <View className="flex-row justify-between items-center mb-4">
                    <Text className="text-gray-700">Furnished</Text>
                    <Switch
                      trackColor={{ false: "#d1d5db", true: "#bfdbfe" }}
                      thumbColor={filters.furnished ? "#3b82f6" : "#f4f3f4"}
                      value={filters.furnished}
                      onValueChange={(value) => setFilters({...filters, furnished: value})}
                    />
                  </View>
                  
                  <View className="flex-row justify-between items-center">
                    <Text className="text-gray-700">Pets Allowed</Text>
                    <Switch
                      trackColor={{ false: "#d1d5db", true: "#bfdbfe" }}
                      thumbColor={filters.pets ? "#3b82f6" : "#f4f3f4"}
                      value={filters.pets}
                      onValueChange={(value) => setFilters({...filters, pets: value})}
                    />
                  </View>
                </View>
              </ScrollView>

              {/* Apply Button */}
              <View className="p-4">
                <TouchableOpacity 
                  className="bg-blue-500 p-4 rounded-lg items-center"
                  onPress={handleApplyFilters}
                >
                  <Text className="text-white font-bold text-lg">Apply Filters</Text>
                </TouchableOpacity>
              </View>
            </View>
          </TouchableWithoutFeedback>
        </View>
      </TouchableWithoutFeedback>
    </Modal>
  );
} 