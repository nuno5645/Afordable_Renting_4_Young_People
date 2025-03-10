import React from 'react';
import { View, Text, Image, TouchableOpacity } from 'react-native';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { styled } from '../theme';

// Styled components
const StyledView = styled(View);
const StyledText = styled(Text);
const StyledTouchableOpacity = styled(TouchableOpacity);

export default function PropertyCard({ property }) {
  return (
    <StyledView className="bg-black/5 dark:bg-white/10 rounded-xl mb-4 overflow-hidden">
      {/* Property Image Section */}
      <StyledView className="relative">
        <Image 
          source={{ uri: property.imageUrl }}
          style={{ width: '100%', height: 192 }}
          resizeMode="cover"
        />
        
        {/* Left and Right Navigation Arrows */}
        <StyledTouchableOpacity className="absolute top-1/2 left-2 -translate-y-1/2 h-8 w-8 bg-white/80 rounded-full items-center justify-center">
          <Ionicons name="chevron-back" size={24} color="#333" />
        </StyledTouchableOpacity>
        
        <StyledTouchableOpacity className="absolute top-1/2 right-2 -translate-y-1/2 h-8 w-8 bg-white/80 rounded-full items-center justify-center">
          <Ionicons name="chevron-forward" size={24} color="#333" />
        </StyledTouchableOpacity>
        
        {/* Favorite Button */}
        <StyledTouchableOpacity className="absolute top-2 right-2 h-8 w-8 bg-white/80 rounded-full items-center justify-center">
          <Ionicons name="heart-outline" size={22} color="#333" />
        </StyledTouchableOpacity>
        
        {/* Current Image Indicator */}
        <StyledView className="absolute bottom-2 left-0 right-0 flex-row justify-center">
          <StyledText className="text-xs text-white bg-black/40 px-2 py-0.5 rounded-full">
            {property.currentImage}/{property.totalImages}
          </StyledText>
        </StyledView>
      </StyledView>
      
      {/* Property Info Section */}
      <StyledView className="p-3">
        {/* Info Icon */}
        <StyledView className="flex-row items-center mb-1">
          <StyledView className="h-6 w-6 bg-gray-300 rounded-full items-center justify-center mr-2">
            <Ionicons name="information" size={16} color="#333" />
          </StyledView>
          <StyledText className="text-xs text-gray-700 flex-1" numberOfLines={2}>{property.address}</StyledText>
        </StyledView>
        
        {/* Price */}
        <StyledText className="text-lg font-bold">€{property.price}/month</StyledText>
        
        {/* Attributes */}
        <StyledView className="flex-row items-center justify-between mt-1">
          <StyledView className="flex-row items-center">
            <Ionicons name="car-outline" size={16} color="#666" />
            <StyledText className="ml-1 text-xs text-gray-700">{property.parkingSpots}</StyledText>
          </StyledView>
          
          <StyledView className="flex-row items-center">
            <StyledText className="text-xs text-gray-700">{property.area} m²</StyledText>
          </StyledView>
          
          <StyledText className="text-xs text-gray-500">{property.source}</StyledText>
        </StyledView>
      </StyledView>
      
      {/* Action Buttons */}
      <StyledView className="flex-row border-t border-gray-200">
        <StyledTouchableOpacity className="flex-1 items-center justify-center py-2 flex-row">
          <Ionicons name="eye-outline" size={18} color="#3b82f6" />
          <StyledText className="text-sm font-medium text-blue-500 ml-1">Visit</StyledText>
        </StyledTouchableOpacity>
        
        <StyledView className="w-px bg-gray-200" />
        
        <StyledTouchableOpacity className="w-10 items-center justify-center py-2">
          <Ionicons name="mail-outline" size={18} color="#666" />
        </StyledTouchableOpacity>
        
        <StyledView className="w-px bg-gray-200" />
        
        <StyledTouchableOpacity className="w-10 items-center justify-center py-2">
          <Ionicons name="trash-outline" size={18} color="#666" />
        </StyledTouchableOpacity>
      </StyledView>
    </StyledView>
  );
} 