import { View, Text, ScrollView, TouchableOpacity } from "react-native";

export default function PortfolioScreen() {
  return (
    <ScrollView className="flex-1 bg-dark-900">
      <View className="px-5 pt-12 pb-6">
        <Text className="text-white text-2xl font-bold mb-1">Portfolio</Text>
        <Text className="text-dark-600 mb-6">
          Your trading dashboard
        </Text>

        {/* Balance Card */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4 border border-dark-700">
          <Text className="text-dark-600 text-sm mb-1">Total Balance</Text>
          <Text className="text-white text-3xl font-bold">$0.00</Text>
          <View className="flex-row mt-3">
            <View className="flex-1">
              <Text className="text-dark-600 text-xs">Available</Text>
              <Text className="text-white text-lg font-semibold">$0.00</Text>
            </View>
            <View className="flex-1">
              <Text className="text-dark-600 text-xs">24h P&L</Text>
              <Text className="text-brand-400 text-lg font-semibold">
                +$0.00
              </Text>
            </View>
          </View>
        </View>

        {/* Open Positions */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4 border border-dark-700">
          <Text className="text-white text-lg font-semibold mb-3">
            Open Positions
          </Text>
          <View className="items-center py-8">
            <Text className="text-dark-600">
              No open positions yet
            </Text>
            <Text className="text-dark-600 text-sm mt-1">
              Connect an exchange to start trading
            </Text>
          </View>
        </View>

        {/* Quick Actions */}
        <View className="flex-row gap-3 mb-4">
          <TouchableOpacity className="flex-1 bg-brand-600 py-3 rounded-xl items-center">
            <Text className="text-white font-semibold">Deposit</Text>
          </TouchableOpacity>
          <TouchableOpacity className="flex-1 bg-dark-700 py-3 rounded-xl items-center">
            <Text className="text-white font-semibold">Withdraw</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}
