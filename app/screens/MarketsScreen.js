import { View, Text, ScrollView, TouchableOpacity } from "react-native";

const WATCHLIST = [
  { symbol: "BTC", name: "Bitcoin", price: 64234.56, change: 2.34, color: "text-brand-400" },
  { symbol: "ETH", name: "Ethereum", price: 3456.78, change: -1.23, color: "text-white" },
  { symbol: "SOL", name: "Solana", price: 145.23, change: 5.67, color: "text-brand-400" },
  { symbol: "BNB", name: "BNB", price: 567.89, change: 0.45, color: "text-white" },
  { symbol: "XRP", name: "Ripple", price: 0.5234, change: -2.15, color: "text-red-500" },
];

const ALERTS = [
  { symbol: "BTC", condition: "Price above", value: "$65,000", active: true },
  { symbol: "ETH", condition: "Price below", value: "$3,200", active: false },
  { symbol: "SOL", condition: "+10% change", value: "24h", active: true },
];

export default function MarketsScreen() {
  const fearGreedValue = 65;
  const fearGreedLabel = "Greed";

  return (
    <ScrollView className="flex-1 bg-dark-900">
      <View className="px-5 pt-12 pb-6">
        {/* Header */}
        <Text className="text-white text-2xl font-bold mb-1">Markets</Text>
        <Text className="text-dark-600 mb-6">Real-time crypto prices</Text>

        {/* Fear & Greed Index */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4 border border-dark-700">
          <Text className="text-white text-lg font-semibold mb-4">Fear & Greed Index</Text>
          <View className="items-center">
            <View className="w-32 h-32 rounded-full border-4 border-dark-700 items-center justify-center mb-3">
              <Text className="text-4xl font-bold text-brand-400">{fearGreedValue}</Text>
            </View>
            <View className="bg-brand-900 px-4 py-1 rounded-full">
              <Text className="text-brand-400 font-semibold text-sm">{fearGreedLabel}</Text>
            </View>
            <Text className="text-dark-600 text-sm mt-3">Last updated: 5 min ago</Text>
          </View>
          
          {/* Gauge indicator */}
          <View className="mt-4">
            <View className="h-2 rounded-full bg-gradient-to-r from-red-600 via-yellow-500 to-green-600" />
            <View className="flex-row justify-between mt-1">
              <Text className="text-dark-600 text-xs">Extreme Fear</Text>
              <Text className="text-dark-600 text-xs">Neutral</Text>
              <Text className="text-dark-600 text-xs">Extreme Greed</Text>
            </View>
          </View>
        </View>

        {/* Watchlist */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4 border border-dark-700">
          <View className="flex-row justify-between items-center mb-4">
            <Text className="text-white text-lg font-semibold">Watchlist</Text>
            <TouchableOpacity>
              <Text className="text-brand-400 text-sm">+ Add</Text>
            </TouchableOpacity>
          </View>

          {/* Table header */}
          <View className="flex-row justify-between mb-3 pb-2 border-b border-dark-700">
            <Text className="text-dark-600 text-sm w-20">Asset</Text>
            <Text className="text-dark-600 text-sm text-right">Price</Text>
            <Text className="text-dark-600 text-sm text-right w-20">24h</Text>
          </View>

          {WATCHLIST.map((coin) => (
            <TouchableOpacity
              key={coin.symbol}
              className="flex-row justify-between items-center py-3 border-b border-dark-700 last:border-0"
            >
              <View className="flex-row items-center gap-3 w-40">
                <View className="w-10 h-10 bg-dark-700 rounded-full items-center justify-center">
                  <Text className="text-white font-bold text-sm">{coin.symbol[0]}</Text>
                </View>
                <View>
                  <Text className="text-white font-semibold">{coin.symbol}</Text>
                  <Text className="text-dark-600 text-xs">{coin.name}</Text>
                </View>
              </View>
              <Text className="text-white font-semibold">
                ${coin.price.toLocaleString()}
              </Text>
              <View className={`w-20 text-right`}>
                <Text className={`${coin.change >= 0 ? "text-brand-400" : "text-red-500"} font-semibold`}>
                  {coin.change >= 0 ? "+" : ""}{coin.change}%
                </Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Price Alerts */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4 border border-dark-700">
          <View className="flex-row justify-between items-center mb-4">
            <Text className="text-white text-lg font-semibold">Price Alerts</Text>
            <TouchableOpacity>
              <Text className="text-brand-400 text-sm">+ Create</Text>
            </TouchableOpacity>
          </View>

          {ALERTS.map((alert, index) => (
            <View
              key={index}
              className="flex-row justify-between items-center py-3 border-b border-dark-700 last:border-0"
            >
              <View className="flex-row items-center gap-3">
                <View className={`w-3 h-3 rounded-full ${alert.active ? "bg-brand-400" : "bg-dark-600"}`} />
                <View>
                  <Text className="text-white font-semibold">{alert.symbol}</Text>
                  <Text className="text-dark-600 text-sm">{alert.condition} {alert.value}</Text>
                </View>
              </View>
              <TouchableOpacity className="px-3 py-1">
                <Text className="text-red-500 text-sm">✕</Text>
              </TouchableOpacity>
            </View>
          ))}
        </View>

        {/* Market Overview Stats */}
        <View className="flex-row gap-3">
          <View className="flex-1 bg-dark-800 rounded-xl p-4 border border-dark-700">
            <Text className="text-dark-600 text-xs mb-1">Total Market Cap</Text>
            <Text className="text-white text-lg font-bold">$2.34T</Text>
          </View>
          <View className="flex-1 bg-dark-800 rounded-xl p-4 border border-dark-700">
            <Text className="text-dark-600 text-xs mb-1">24h Volume</Text>
            <Text className="text-white text-lg font-bold">$78.5B</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}