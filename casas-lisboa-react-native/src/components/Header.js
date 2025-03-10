import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { styled } from '../theme';

// Styled components
const StyledView = styled(View);
const StyledText = styled(Text);
const StyledTouchableOpacity = styled(TouchableOpacity);

export default function Header({ title, showFilter = true, filterCount = 0, onFilterPress }) {
  return (
    <StyledView className="bg-white p-4 flex-row items-center justify-between shadow-sm">
      <StyledText className="text-xl font-bold">{title}</StyledText>
      {showFilter && (
        <StyledTouchableOpacity 
          className="p-2 relative" 
          onPress={onFilterPress}
        >
          <Ionicons name="options-outline" size={24} color="#333" />
          {filterCount > 0 && (
            <StyledView className="absolute -top-1 -right-1 bg-blue-500 rounded-full w-4 h-4 items-center justify-center">
              <StyledText className="text-[10px] text-white">{filterCount}</StyledText>
            </StyledView>
          )}
        </StyledTouchableOpacity>
      )}
    </StyledView>
  );
} 