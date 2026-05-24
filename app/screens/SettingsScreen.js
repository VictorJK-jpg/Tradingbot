import { View, Text, TouchableOpacity, Alert, ScrollView, Switch } from "react-native";
import { useState } from "react";

import useAuthStore from "../store/authStore";
import api from "../services/api";

export default function SettingsScreen() {
  const clearTokens = useAuthStore((s) => s.clearTokens);
  const [notifications, setNotifications] = useState({
    priceAlerts: true,
    aiSuggestions: true,
    weeklyReport: false,
    marketNews: true,
  });
  const [loading, setLoading] = useState(false);

  const handleLogout = () => {
    Alert.alert("Sign Out", "Are you sure you want to sign out?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Sign Out",
        style: "destructive",
        onPress: () => clearTokens(),
      },
    ]);
  };

  const handleRefreshToken = async () => {
    setLoading(true);
    try {
      const tokens = useAuthStore.getState().tokens;
      if (tokens?.refresh_token) {
        const response = await api.post("/auth/refresh", {
          refresh_token: tokens.refresh_token,
        });
        await useAuthStore.getState().setTokens(response.data);
        Alert.alert("Success", "Token refreshed");
      }
    } catch (err) {
      Alert.alert("Error", "Failed to refresh token");
    } finally {
      setLoading(false);
    }
  };

  const SettingItem = ({ title, subtitle, onPress, icon, danger = false }) => (
    <TouchableOpacity
      onPress={onPress}
      className="flex-row items-center justify-between px-5 py-4 border-b border-dark-700"
    >
      <View className="flex-row items-center gap-4">
        <Text className="text-2xl">{icon}</Text>
        <View>
          <Text className={`font-semibold ${danger ? "text-red-400" : "text-white"}`}>
            {title}
          </Text>
          {subtitle && (
            <Text className="text-dark-600 text-sm">{subtitle}</Text>
          )}
        </View>
      </View>
      {!danger && <Text className="text-dark-600">›</Text>}
    </TouchableOpacity>
  );

  const ToggleItem = ({ title, value, onToggle, icon }) => (
    <View className="flex-row items-center justify-between px-5 py-4 border-b border-dark-700">
      <View className="flex-row items-center gap-4">
        <Text className="text-2xl">{icon}</Text>
        <Text className="text-white font-semibold">{title}</Text>
      </View>
      <Switch
        value={value}
        onValueChange={onToggle}
        trackColor={{ false: "#1e293b", true: "#4ade80" }}
        thumbColor="#fff"
      />
    </View>
  );

  return (
    <ScrollView className="flex-1 bg-dark-900">
      <View className="px-5 pt-12 pb-6">
        {/* Header */}
        <Text className="text-white text-2xl font-bold mb-1">Settings</Text>
        <Text className="text-dark-600 mb-6">Manage your account and preferences</Text>

        {/* Account Section */}
        <Text className="text-dark-600 text-sm mb-2 uppercase tracking-wider">Account</Text>
        <View className="bg-dark-800 rounded-2xl border border-dark-700 overflow-hidden mb-6">
          <SettingItem
            icon="👤"
            title="Edit Profile"
            subtitle="Name, email, and avatar"
            onPress={() => Alert.alert("Coming Soon", "Profile editing in development")}
          />
          <SettingItem
            icon="🔑"
            title="Change Password"
            subtitle="Update your security"
            onPress={() => Alert.alert("Coming Soon", "Password change in development")}
          />
          <SettingItem
            icon="🤖"
            title="AI Preferences"
            subtitle="Model and response settings"
            onPress={() => Alert.alert("Coming Soon", "AI preferences in development")}
          />
        </View>

        {/* Trading Section */}
        <Text className="text-dark-600 text-sm mb-2 uppercase tracking-wider">Trading</Text>
        <View className="bg-dark-800 rounded-2xl border border-dark-700 overflow-hidden mb-6">
          <SettingItem
            icon="📊"
            title="Risk Budget"
            subtitle="Max risk per trade and daily limits"
            onPress={() => Alert.alert("Coming Soon", "Risk settings in development")}
          />
          <SettingItem
            icon="🔗"
            title="Exchange Connections"
            subtitle="Manage API keys"
            onPress={() => Alert.alert("Coming Soon", "Exchange settings in development")}
          />
          <SettingItem
            icon="📋"
            title="Trading Rules"
            subtitle="Style and preferred assets"
            onPress={() => Alert.alert("Coming Soon", "Trading rules in development")}
          />
        </View>

        {/* Notifications Section */}
        <Text className="text-dark-600 text-sm mb-2 uppercase tracking-wider">Notifications</Text>
        <View className="bg-dark-800 rounded-2xl border border-dark-700 overflow-hidden mb-6">
          <ToggleItem
            icon="🔔"
            title="Price Alerts"
            value={notifications.priceAlerts}
            onToggle={(v) => setNotifications({ ...notifications, priceAlerts: v })}
          />
          <ToggleItem
            icon="🤖"
            title="AI Trade Suggestions"
            value={notifications.aiSuggestions}
            onToggle={(v) => setNotifications({ ...notifications, aiSuggestions: v })}
          />
          <ToggleItem
            icon="📊"
            title="Weekly Market Report"
            value={notifications.weeklyReport}
            onToggle={(v) => setNotifications({ ...notifications, weeklyReport: v })}
          />
          <ToggleItem
            icon="📰"
            title="Market News"
            value={notifications.marketNews}
            onToggle={(v) => setNotifications({ ...notifications, marketNews: v })}
          />
        </View>

        {/* Security Section */}
        <Text className="text-dark-600 text-sm mb-2 uppercase tracking-wider">Security</Text>
        <View className="bg-dark-800 rounded-2xl border border-dark-700 overflow-hidden mb-6">
          <SettingItem
            icon="🔄"
            title="Refresh Token"
            subtitle="Get a new access token"
            onPress={handleRefreshToken}
          />
          <SettingItem
            icon="📱"
            title="Two-Factor Auth"
            subtitle="Not enabled"
            onPress={() => Alert.alert("Coming Soon", "2FA in development")}
          />
          <SettingItem
            icon="🔒"
            title="Biometric Login"
            subtitle="Use fingerprint to login"
            onPress={() => Alert.alert("Coming Soon", "Biometric in development")}
          />
        </View>

        {/* About Section */}
        <Text className="text-dark-600 text-sm mb-2 uppercase tracking-wider">About</Text>
        <View className="bg-dark-800 rounded-2xl border border-dark-700 overflow-hidden mb-6">
          <SettingItem
            icon="📱"
            title="App Version"
            subtitle="1.0.0 (Build 1)"
            onPress={() => {}}
          />
          <SettingItem
            icon="📄"
            title="Terms of Service"
            onPress={() => Alert.alert("Coming Soon", "Terms in development")}
          />
          <SettingItem
            icon="🔒"
            title="Privacy Policy"
            onPress={() => Alert.alert("Coming Soon", "Privacy in development")}
          />
        </View>

        {/* Sign Out */}
        <TouchableOpacity
          onPress={handleLogout}
          className="bg-red-900/20 py-4 rounded-xl items-center border border-red-900/30 mb-6"
        >
          <Text className="text-red-400 font-semibold text-lg">Sign Out</Text>
        </TouchableOpacity>

        {/* Footer */}
        <View className="items-center pt-4 pb-8">
          <Text className="text-dark-600 text-sm">Crypto Platform v1.0.0</Text>
          <Text className="text-dark-700 text-xs mt-1">Made with ❤️ for traders</Text>
        </View>
      </View>
    </ScrollView>
  );
}
