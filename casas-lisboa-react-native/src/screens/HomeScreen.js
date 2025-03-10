import React, { useState } from 'react';
import { View, FlatList, SafeAreaView, StatusBar } from 'react-native';
import PropertyCard from '../components/PropertyCard';
import Header from '../components/Header';
import FilterModal from '../components/FilterModal';
import { styled } from '../theme';

// Styled components
const StyledView = styled(View);
const StyledSafeAreaView = styled(SafeAreaView);
const StyledFlatList = styled(FlatList);

// Sample data
const properties = [
  {
    id: '1',
    imageUrl: 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267',
    address: 'Avenida Embaixador Augusto de Castro, 23, Figueirinha - Augusto Castro, Oeiras e São Julião da Barra, Oeiras e São Julião da Barra, Paço de Arcos - Caxias',
    price: '900',
    parkingSpots: '0',
    area: '0.00',
    source: 'Idealista',
    currentImage: '1',
    totalImages: '3'
  },
  {
    id: '2',
    imageUrl: 'https://images.unsplash.com/photo-1493809842364-78817add7ffb',
    address: 'Rua Marquês de Pombal, 45, Belém, Lisboa',
    price: '1200',
    parkingSpots: '1',
    area: '75.00',
    source: 'Idealista',
    currentImage: '2',
    totalImages: '5'
  },
  {
    id: '3',
    imageUrl: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688',
    address: 'Avenida da Liberdade, 120, Avenidas Novas, Lisboa',
    price: '1500',
    parkingSpots: '1',
    area: '90.00',
    source: 'Idealista',
    currentImage: '1',
    totalImages: '4'
  }
];

export default function HomeScreen() {
  const [activeFilters, setActiveFilters] = useState(3);
  const [filterModalVisible, setFilterModalVisible] = useState(false);
  const [filteredProperties, setFilteredProperties] = useState(properties);

  const handleFilterPress = () => {
    setFilterModalVisible(true);
  };

  const handleApplyFilters = (filters) => {
    console.log('Applied filters:', filters);
    // In a real app, we would filter properties based on the criteria
    // For now, we'll just keep the original list
    setFilteredProperties(properties);
    // Count how many filters are applied
    const count = Object.values(filters).filter(value => {
      if (Array.isArray(value) && value.every(v => v === 0)) return false;
      return value === true || (typeof value === 'number' && value > 0);
    }).length;
    setActiveFilters(count);
  };

  return (
    <StyledSafeAreaView className="flex-1 bg-gray-50">
      <StatusBar barStyle="dark-content" backgroundColor="#fff" />
      
      {/* Header */}
      <Header 
        title="Lisbon Rentals" 
        filterCount={activeFilters}
        onFilterPress={handleFilterPress}
      />
      
      {/* Property List */}
      <StyledFlatList
        data={filteredProperties}
        keyExtractor={item => item.id}
        contentContainerStyle={{ padding: 16 }}
        renderItem={({ item }) => (
          <PropertyCard property={item} />
        )}
      />

      {/* Filter Modal */}
      <FilterModal 
        visible={filterModalVisible}
        onClose={() => setFilterModalVisible(false)}
        onApply={handleApplyFilters}
      />
    </StyledSafeAreaView>
  );
} 