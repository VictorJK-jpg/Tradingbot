import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Text, View } from "react-native";

import useAuthStore from "../store/authStore";

// Auth screens
import LoginScreen from "../screens/LoginScreen";
import RegisterScreen from "../screens/RegisterScreen";

// Onboarding
import OnboardingNavigator from "./OnboardingNavigator";

// Main screens
import HomeScreen from "../screens/HomeScreen";
import AIChatScreen from "../screens/AIChatScreen";
import PortfolioScreen from "../screens/PortfolioScreen";
import MarketsScreen from "../screens/MarketsScreen";
import SettingsScreen from "../screens/SettingsScreen";

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Tab icon component
function TabIcon({ name, focused }) {
  const icons = {
    Home: "🏠",
    Chat: "🤖",
    Portfolio: "📊",
    Markets: "📈",
    Settings: "⚙️",
  };
  return (
    <View className="items-center">
      <Text className="text-xl">{icons[name]}</Text>
      <Text className={`text-xs mt-1 ${focused ? "text-brand-400" : "text-dark-600"}`}>
        {name}
      </Text>
    </View>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarStyle: {
          backgroundColor: "#0f172a",
          borderTopColor: "#1e293b",
          height: 80,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarShowLabel: false,
        tabBarActiveTintColor: "#4ade80",
        tabBarInactiveTintColor: "#64748b",
        tabBarIcon: ({ focused }) => <TabIcon name={route.name} focused={focused} />,
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Chat" component={AIChatScreen} />
      <Tab.Screen name="Portfolio" component={PortfolioScreen} />
      <Tab.Screen name="Markets" component={MarketsScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}

export default function AppNavigator() {
  const tokens = useAuthStore((s) => s.tokens);
  const isLoading = useAuthStore((s) => s.isLoading);

  if (isLoading) {
    return (
      <View className="flex-1 bg-dark-900 items-center justify-center">
        <Text className="text-white text-lg">Loading...</Text>
      </View>
    );
  }

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {!tokens ? (
        <>
          <Stack.Screen 
            name="Login" 
            component={LoginScreen}
            options={{ animation: "fade" }}
          />
          <Stack.Screen 
            name="Register" 
            component={RegisterScreen}
            options={{ animation: "fade" }}
          />
        </>
      ) : (
        <>
          <Stack.Screen 
            name="Onboarding" 
            component={OnboardingNavigator}
            options={{ animation: "slide_from_right" }}
          />
          <Stack.Screen 
            name="Main" 
            component={MainTabs}
            options={{ animation: "fade" }}
          />
        </>
      )}
    </Stack.Navigator>
  );
}
