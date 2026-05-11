import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, ScrollView } from "react-native";
import { useNavigation } from "@react-navigation/native";

import api from "../../services/api";

const POPULAR_ASSETS = ["BTC", "ETH", "SOL", "AVAX", "LINK", "UNI", "ARB", "OP"];

export default function OnboardingAssetsScreen() {
  const navigation = useNavigation();
  const [preferred, setPreferred] = useState([]);
  const [blacklist, setBlacklist] = useState([]);
  const [customAsset, setCustomAsset] = useState("");
  const [loading, setLoading] = useState(false);

  const toggleAsset = (asset, list, setList) => {
    setList((prev) =>
      prev.includes(asset) ? prev.filter((a) => a !== asset) : [...prev, asset]
    );
  };

  const addCustom = () => {
    const symbol = customAsset.trim().toUpperCase();
    if (symbol && !preferred.includes(symbol)) {
      setPreferred((prev) => [...prev, symbol]);
      setCustomAsset("");
    }
  };

  const handleNext = async () => {
    setLoading(true);
    try {
      await api.post("/onboarding/step-6", { preferred_assets: preferred, blacklist_assets: blacklist });
      navigation.navigate("OnboardingExchange");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView className="flex-1 bg-dark-900">
      <View className="px-6 pt-12 pb-6">
        <Text className="text-brand-400 text-sm font-semibold mb-2">Step 6 of 9</Text>
        <Text className="text-white text-2xl font-bold mb-2">Asset Preferences</Text>
        <Text className="text-dark-600 mb-6">
          Pick assets you want to track. Blacklist anything you never trade.
        </Text>

        {/* Preferred */}
        <Text className="text-white font-semibold mb-3">Preferred Assets</Text>
        <View className="flex-row flex-wrap gap-2 mb-4">
          {POPULAR_ASSETS.map((asset) => (
            <TouchableOpacity
              key={asset}
              onPress={() => toggleAsset(asset, preferred, setPreferred)}
              className={`px-4 py-2 rounded-xl border ${
                preferred.includes(asset)
                  ? "bg-brand-500 border-brand-500"
                  : "bg-dark-800 border-dark-700"
              }`}
            >
              <Text
                className={`font-semibold ${
                  preferred.includes(asset) ? "text-white" : "text-dark-600"
                }`}
              >
                {asset}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <View className="flex-row gap-2 mb-6">
          <TextInput
            className="flex-1 bg-dark-800 text-white px-4 py-2 rounded-xl border border-dark-700"
            placeholder="Add custom asset (e.g. PEPE)"
            placeholderTextColor="#64748b"
            autoCapitalize="characters"
            value={customAsset}
            onChangeText={setCustomAsset}
          />
          <TouchableOpacity
            onPress={addCustom}
            className="bg-dark-700 px-4 rounded-xl items-center justify-center"
          >
            <Text className="text-white font-semibold">Add</Text>
          </TouchableOpacity>
        </View>

        {/* Blacklist */}
        <Text className="text-white font-semibold mb-3">Blacklist</Text>
        <Text className="text-dark-600 text-sm mb-3">
          Assets the AI should never suggest
        </Text>
        <View className="flex-row flex-wrap gap-2 mb-6">
          {POPULAR_ASSETS.map((asset) => (
            <TouchableOpacity
              key={asset}
              onPress={() => toggleAsset(asset, blacklist, setBlacklist)}
              className={`px-4 py-2 rounded-xl border ${
                blacklist.includes(asset)
                  ? "bg-red-500 border-red-500"
                  : "bg-dark-800 border-dark-700"
              }`}
            >
              <Text
                className={`font-semibold ${
                  blacklist.includes(asset) ? "text-white" : "text-dark-600"
                }`}
              >
                {asset}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <TouchableOpacity
          onPress={handleNext}
          disabled={loading}
          className="bg-brand-500 py-4 rounded-xl items-center"
        >
          <Text className="text-white font-semibold text-lg">
            {loading ? "Saving..." : "Next"}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}
