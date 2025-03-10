//import React from 'react';
//import { SafeAreaProvider } from 'react-native-safe-area-context';
//import { LogBox } from 'react-native';
//import 'react-native-reanimated';
//import Navigation from './src/navigation';
//
//// Ignore specific warnings that might be coming from dependencies
//LogBox.ignoreLogs([
//  'Reanimated 2',
//  'EventEmitter.removeListener',
//  'ViewPropTypes will be removed'
//]);
//
//export default function App() {
//  return (
//    <SafeAreaProvider>
//      <Navigation />
//    </SafeAreaProvider>
//  );
//}

import React from 'react';
import { View, Text } from 'react-native';

export default function App() {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Hello World!</Text>
    </View>
  );
}
