import { View, Text, ScrollView, TouchableOpacity } from "react-native";

const POSITIONS = [
  {
    symbol: "BTC",
    pair: "BTC/USDT",
    side: "Long",
    entryPrice: 63500,
    markPrice: 64234.56,
    size: 0.5,
    pnl: 420.50,
    pnlPercent: 2.1,
    leverage: "5x",
  },
  {
    symbol: "ETH",
    pair: "ETH/USDT",
    side: "Long",
    entryPrice: 3200,
    markPrice: 3456.78,
    size: 2,
    pnl: -85.20,
    pnlPercent: -0.8,
    leverage: "3x",
  },
];

const TRADE_HISTORY = [
  { date: "May 23", pair: "SOL/USDT", side: "Long", pnl: 125.50, pnlPercent: 3.2 },
  { date: "May 22", pair: "AVAX/USDT", side: "Short", pnl: -45.00, pnlPercent: -1.1 },
  { date: "May 21", pair: "BNB/USDT", side: "Long", pnl: 210.00, pnlPercent: 4.5 },
  { date: "May 20", pair: "BTC/USDT", side: "Short", pnl: 340.75, pnlPercent: 1.8 },
];

export default function PortfolioScreen() {
  return (
    <ScrollView className="flex-1 bg-dark-900">
      <View className="px-5 pt-12 pb-6">
        {/* Header */}
        <View className="flex-row justify-between items-center mb-6">
          <View>
            <Text className="text-white text-2xl font-bold">Portfolio</Text>
            <Text className="text-dark-600 text-sm">Your trading dashboard</Text>
          </View>
          <TouchableOpacity className="bg-dark-800 px-4 py-2 rounded-xl">
            <Text className="text-brand-400 text-sm font-semibold">Export</Text>
          </TouchableOpacity>
        </View>

        {/* Balance Card */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4 border border-dark-700">
          <View className="flex-row justify-between items-start mb-4">
            <View>
              <Text className="text-dark-600 text-sm mb-1">Total Balance</Text>
              <Text className="text-white text-3xl font-bold">$10,245.67</Text>
            </View>
            <View className="bg-brand-900 px-3 py-1 rounded-lg">
              <Text className="text-brand-400 text-sm font-semibold">+12.4%</Text>
            </View>
          </View>
          
          <View className="flex-row gap-4 mb-4">
            <View className="flex-1">
              <Text className="text-dark-600 text-xs mb-1">Available</Text>
              <Text className="text-white text-lg font-semibold">$8,245.67</Text>
            </View>
            <View className="flex-1">
              <Text className="text-dark-600 text-xs mb-1">24h P&L</Text>
              <Text className="text-brand-400 text-lg font-semibold">+$1,234.00</Text>
            </View>
          </View>

          {/* Quick Actions */}
          <View className="flex-row gap-3 mt-4 pt-4 border-t border-dark-700">
            <TouchableOpacity className="flex-1 bg-brand-600 py-3 rounded-xl items-center">
              <Text className="text-white font-semibold">Deposit</Text>
            </TouchableOpacity>
            <TouchableOpacity className="flex-1 bg-dark-700 py-3 rounded-xl items-center">
              <Text className="text-white font-semibold">Withdraw</Text>
            </TouchableOpacity>
            <TouchableOpacity className="flex-1 bg-dark-700 py-3 rounded-xl items-center">
              <Text className="text-white font-semibold">Transfer</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Stats Row */}
        <View className="flex-row gap-3 mb-4">
          <View className="flex-1 bg-dark-800 rounded-xl p-4 border border-dark-700">
            <Text className="text-dark-600 text-xs mb-1">Unrealized P&L</Text>
            <Text className="text-brand-400 text-lg font-bold">+$335.30</Text>
          </View>
          <View className="flex-1 bg-dark-800 rounded-xl p-4 border border-dark-700">
            <Text className="text-dark-600 text-xs mb-1">Win Rate</Text>
            <Text className="text-white text-lg font-bold">68%</Text>
          </View>
          <View className="flex-1 bg-dark-800 rounded-xl p-4 border border-dark-700">
            <Text className="text-dark-600 text-xs mb-1">Open Positions</Text>
            <Text className="text-white text-lg font-bold">{POSITIONS.length}</Text>
          </View>
        </View>

        {/* Open Positions */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4 border border-dark-700">
          <View className="flex-row justify-between items-center mb-4">
            <Text className="text-white text-lg font-semibold">Open Positions</Text>
            <TouchableOpacity>
              <Text className="text-brand-400 text-sm">View All</Text>
            </TouchableOpacity>
          </View>

          {POSITIONS.map((pos, index) => (
            <View
              key={index}
              className="py-4 border-b border-dark-700 last:border-0"
            >
              <View className="flex-row justify-between items-start mb-2">
                <View className="flex-row items-center gap-3">
                  <View className="w-10 h-10 bg-dark-700 rounded-full items-center justify-center">
                    <Text className="text-white font-bold text-sm">{pos.symbol}</Text>
                  </View>
                  <View>
                    <Text className="text-white font-semibold">{pos.pair}</Text>
                    <Text className="text-dark-600 text-sm">{pos.side} • {pos.leverage}</Text>
                  </View>
                </View>
                <View className="items-end">
                  <Text className={`font-semibold ${pos.pnl >= 0 ? "text-brand-400" : "text-red-500"}`}>
                    {pos.pnl >= 0 ? "+" : ""}${pos.pnl.toFixed(2)}
                  </Text>
                  <Text className={`text-sm ${pos.pnl >= 0 ? "text-brand-400" : "text-red-500"}`}>
                    {pos.pnl >= 0 ? "+" : ""}{pos.pnlPercent}%
                  </Text>
                </View>
              </View>
              <View className="flex-row gap-4 mt-2">
                <View>
                  <Text className="text-dark-600 text-xs">Entry</Text>
                  <Text className="text-white text-sm">${pos.entryPrice.toLocaleString()}</Text>
                </View>
                <View>
                  <Text className="text-dark-600 text-xs">Mark</Text>
                  <Text className="text-white text-sm">${pos.markPrice.toLocaleString()}</Text>
                </View>
                <View>
                  <Text className="text-dark-600 text-xs">Size</Text>
                  <Text className="text-white text-sm">{pos.size}</Text>
                </View>
              </View>
            </View>
          ))}
        </View>

        {/* Trade History */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4 border border-dark-700">
          <View className="flex-row justify-between items-center mb-4">
            <Text className="text-white text-lg font-semibold">Recent Trades</Text>
            <TouchableOpacity>
              <Text className="text-brand-400 text-sm">Full History</Text>
            </TouchableOpacity>
          </View>

          {/* Table header */}
          <View className="flex-row justify-between py-2 border-b border-dark-700 mb-2">
            <Text className="text-dark-600 text-sm w-16">Date</Text>
            <Text className="text-dark-600 text-sm flex-1">Pair</Text>
            <Text className="text-dark-600 text-sm text-right w-16">Side</Text>
            <Text className="text-dark-600 text-sm text-right w-20">P&L</Text>
          </View>

          {TRADE_HISTORY.map((trade, index) => (
            <View
              key={index}
              className="flex-row justify-between items-center py-3 border-b border-dark-700 last:border-0"
            >
              <Text className="text-dark-600 text-sm w-16">{trade.date}</Text>
              <Text className="text-white text-sm flex-1">{trade.pair}</Text>
              <Text className={`text-sm text-right w-16 ${trade.side === "Long" ? "text-brand-400" : "text-red-500"}`}>
                {trade.side}
              </Text>
              <Text className={`text-sm text-right w-20 font-semibold ${trade.pnl >= 0 ? "text-brand-400" : "text-red-500"}`}>
                {trade.pnl >= 0 ? "+" : ""}${trade.pnl.toFixed(2)}
              </Text>
            </View>
          ))}
        </View>

        {/* Performance Chart Placeholder */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4 border border-dark-700">
          <Text className="text-white text-lg font-semibold mb-4">30-Day Performance</Text>
          <View className="h-32 flex-row items-end gap-1 justify-between px-2">
            {[40, 55, 45, 60, 50, 70, 65, 80, 75, 90, 85, 95].map((h, i) => (
              <View
                key={i}
                className="flex-1 bg-brand-600 rounded-t"
                style={{ height: `${h}%` }}
              />
            ))}
          </View>
          <View className="flex-row justify-between mt-2">
            <Text className="text-dark-600 text-xs">May 1</Text>
            <Text className="text-dark-600 text-xs">May 15</Text>
            <Text className="text-dark-600 text-xs">May 24</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}
