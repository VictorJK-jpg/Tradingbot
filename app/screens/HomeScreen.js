import { View, Text, ScrollView, TouchableOpacity } from "react-native";

export default function HomeScreen() {
  return (
    <ScrollView className="flex-1 bg-dark-900">
      <View className="px-5 pt-12 pb-6">
        {/* Header */}
        <View className="flex-row justify-between items-center mb-6">
          <View>
            <Text className="text-white text-2xl font-bold">Dashboard</Text>
            <Text className="text-dark-600 text-sm">Welcome back, trader</Text>
          </View>
          <View className="bg-dark-800 px-3 py-2 rounded-xl">
            <Text className="text-brand-400 text-sm font-semibold">Live</Text>
          </View>
        </View>

        {/* Portfolio Summary Card */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4 border border-dark-700">
          <View className="flex-row justify-between items-start mb-4">
            <View>
              <Text className="text-dark-600 text-sm mb-1">Total Portfolio Value</Text>
              <Text className="text-white text-3xl font-bold">$10,245.67</Text>
            </View>
            <View className="bg-brand-900 px-3 py-1 rounded-lg">
              <Text className="text-brand-400 text-sm font-semibold">+12.4%</Text>
            </View>
          </View>
          <View className="flex-row gap-4">
            <View className="flex-1">
              <Text className="text-dark-600 text-xs mb-1">24h Change</Text>
              <Text className="text-brand-400 text-lg font-semibold">+$1,234</Text>
            </View>
            <View className="flex-1">
              <Text className="text-dark-600 text-xs mb-1">Open Positions</Text>
              <Text className="text-white text-lg font-semibold">3</Text>
            </View>
          </View>
        </View>

        {/* Quick Stats Row */}
        <View className="flex-row gap-3 mb-4">
          <View className="flex-1 bg-dark-800 rounded-xl p-4 border border-dark-700">
            <Text className="text-dark-600 text-xs mb-1">Win Rate</Text>
            <Text className="text-white text-xl font-bold">68%</Text>
          </View>
          <View className="flex-1 bg-dark-800 rounded-xl p-4 border border-dark-700">
            <Text className="text-dark-600 text-xs mb-1">AI Budget</Text>
            <Text className="text-white text-xl font-bold">42/50</Text>
          </View>
        </View>

        {/* Recent AI Suggestions */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4 border border-dark-700">
          <View className="flex-row justify-between items-center mb-3">
            <Text className="text-white text-lg font-semibold">Recent AI Suggestions</Text>
            <TouchableOpacity>
              <Text className="text-brand-400 text-sm">View All</Text>
            </TouchableOpacity>
          </View>
          
          {/* Suggestion Card */}
          <View className="bg-dark-700 rounded-xl p-4 mb-3">
            <View className="flex-row justify-between items-start mb-2">
              <Text className="text-white font-semibold">BTC Long Opportunity</Text>
              <View className="bg-brand-900 px-2 py-1 rounded">
                <Text className="text-brand-400 text-xs">Active</Text>
              </View>
            </View>
            <Text className="text-dark-600 text-sm mb-2">
              Entry: $64,500 | Stop: $62,000 | Target: $68,000
            </Text>
            <View className="flex-row gap-2 mt-2">
              <TouchableOpacity className="bg-brand-500 px-4 py-2 rounded-lg">
                <Text className="text-white text-sm font-semibold">Approve</Text>
              </TouchableOpacity>
              <TouchableOpacity className="bg-dark-600 px-4 py-2 rounded-lg">
                <Text className="text-white text-sm">Reject</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Another Suggestion */}
          <View className="bg-dark-700 rounded-xl p-4">
            <View className="flex-row justify-between items-start mb-2">
              <Text className="text-white font-semibold">ETH Momentum Play</Text>
              <View className="bg-dark-600 px-2 py-1 rounded">
                <Text className="text-dark-400 text-xs">Closed</Text>
              </View>
            </View>
            <Text className="text-dark-600 text-sm">
              +3.2% gain on this trade
            </Text>
          </View>
        </View>

        {/* Weekly Outlook Card */}
        <View className="bg-gradient-to-r from-brand-900 to-dark-800 rounded-2xl p-5 mb-4 border border-brand-800">
          <View className="flex-row justify-between items-center mb-2">
            <Text className="text-white text-lg font-semibold">📊 Weekly Outlook</Text>
            <Text className="text-dark-600 text-sm">May 20-26</Text>
          </View>
          <Text className="text-brand-400 text-sm mb-2">Trend: Bullish</Text>
          <Text className="text-dark-400 text-sm">
            DXY weakening, ETF flows positive. Favor long positions with tight stops.
          </Text>
          <TouchableOpacity className="mt-3">
            <Text className="text-brand-400 text-sm font-semibold">Read Full Report →</Text>
          </TouchableOpacity>
        </View>

        {/* Active Positions */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4 border border-dark-700">
          <Text className="text-white text-lg font-semibold mb-3">Active Positions</Text>
          
          {/* Position Row */}
          <View className="flex-row justify-between items-center py-3 border-b border-dark-700">
            <View className="flex-row items-center gap-3">
              <View className="w-10 h-10 bg-dark-700 rounded-full items-center justify-center">
                <Text className="text-white font-bold">BTC</Text>
              </View>
              <View>
                <Text className="text-white font-semibold">BTC/USDT</Text>
                <Text className="text-dark-600 text-sm">Long @ 63,500</Text>
              </View>
            </View>
            <View className="text-right">
              <Text className="text-brand-400 font-semibold">+$420</Text>
              <Text className="text-dark-600 text-sm">+2.1%</Text>
            </View>
          </View>

          {/* Position Row */}
          <View className="flex-row justify-between items-center py-3">
            <View className="flex-row items-center gap-3">
              <View className="w-10 h-10 bg-dark-700 rounded-full items-center justify-center">
                <Text className="text-white font-bold">ETH</Text>
              </View>
              <View>
                <Text className="text-white font-semibold">ETH/USDT</Text>
                <Text className="text-dark-600 text-sm">Long @ 3,200</Text>
              </View>
            </View>
            <View className="text-right">
              <Text className="text-red-500 font-semibold">-$85</Text>
              <Text className="text-dark-600 text-sm">-0.8%</Text>
            </View>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}