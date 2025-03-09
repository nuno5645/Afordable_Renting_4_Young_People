package com.casaslisboa.ui.components

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.tooling.preview.Preview
import com.casaslisboa.ui.theme.LisbonRentalsTheme

sealed class BottomNavItem(val route: String, val icon: ImageVector, val label: String) {
    object Home : BottomNavItem("home", Icons.Filled.Home, "Home")
    object Favorites : BottomNavItem("favorites", Icons.Filled.Favorite, "Favorites")
    object Search : BottomNavItem("search", Icons.Filled.Search, "Search")
    object Analytics : BottomNavItem("analytics", Icons.Filled.Check, "Analytics")
    object Profile : BottomNavItem("profile", Icons.Filled.Person, "Profile")
}

@Composable
fun LisbonRentalsBottomNavigation(
    currentRoute: String,
    onNavigate: (BottomNavItem) -> Unit,
    modifier: Modifier = Modifier
) {
    val items = listOf(
        BottomNavItem.Home,
        BottomNavItem.Favorites,
        BottomNavItem.Search,
        BottomNavItem.Analytics,
        BottomNavItem.Profile
    )

    NavigationBar(
        modifier = modifier
    ) {
        items.forEach { item ->
            NavigationBarItem(
                icon = { Icon(item.icon, contentDescription = item.label) },
                label = { Text(item.label) },
                selected = currentRoute == item.route,
                onClick = { onNavigate(item) }
            )
        }
    }
}

@Preview
@Composable
fun LisbonRentalsBottomNavigationPreview() {
    LisbonRentalsTheme {
        LisbonRentalsBottomNavigation(
            currentRoute = BottomNavItem.Home.route,
            onNavigate = {}
        )
    }
} 