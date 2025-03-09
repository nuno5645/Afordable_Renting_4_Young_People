package com.casaslisboa.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.casaslisboa.model.RentalProperty
import com.casaslisboa.ui.components.BottomNavItem
import com.casaslisboa.ui.screens.FavoritesScreen
import com.casaslisboa.ui.screens.HomeScreen
import com.casaslisboa.ui.screens.StatisticsScreen
import com.casaslisboa.ui.screens.SearchScreen
import com.casaslisboa.ui.screens.ProfileScreen

@Composable
fun Navigation(
    navController: NavHostController,
    properties: List<RentalProperty>,
    onFavoriteClick: (String) -> Unit,
    onEmailClick: (String) -> Unit,
    onDeleteClick: (String) -> Unit,
    onVisitClick: (String) -> Unit,
    onFilterClick: () -> Unit,
) {
    NavHost(
        navController = navController,
        startDestination = BottomNavItem.Home.route
    ) {
        composable(BottomNavItem.Home.route) {
            HomeScreen(
                properties = properties,
                onFavoriteClick = onFavoriteClick,
                onEmailClick = onEmailClick,
                onDeleteClick = onDeleteClick,
                onVisitClick = onVisitClick,
                onFilterClick = onFilterClick,
                onNavigate = { navItem ->
                    navController.navigate(navItem.route) {
                        // Pop up to the start destination of the graph to
                        // avoid building up a large stack of destinations
                        popUpTo(BottomNavItem.Home.route) {
                            saveState = true
                        }
                        // Avoid multiple copies of the same destination
                        launchSingleTop = true
                        // Restore state when navigating back
                        restoreState = true
                    }
                }
            )
        }

        composable(BottomNavItem.Favorites.route) {
            FavoritesScreen(
                favoriteProperties = properties.filter { it.isFavorite },
                onFavoriteClick = onFavoriteClick,
                onEmailClick = onEmailClick,
                onDeleteClick = onDeleteClick,
                onVisitClick = onVisitClick,
                onNavigate = { navItem ->
                    navController.navigate(navItem.route) {
                        popUpTo(BottomNavItem.Home.route) {
                            saveState = true
                        }
                        launchSingleTop = true
                        restoreState = true
                    }
                }
            )
        }

        composable(BottomNavItem.Search.route) {
            SearchScreen(
                onNavigateBack = { navController.navigateUp() },
                onNavigate = { navItem ->
                    navController.navigate(navItem.route) {
                        popUpTo(BottomNavItem.Home.route) {
                            saveState = true
                        }
                        launchSingleTop = true
                        restoreState = true
                    }
                }
            )
        }

        composable(BottomNavItem.Analytics.route) {
            StatisticsScreen(
                onNavigate = { navItem ->
                    navController.navigate(navItem.route) {
                        popUpTo(BottomNavItem.Home.route) {
                            saveState = true
                        }
                        launchSingleTop = true
                        restoreState = true
                    }
                }
            )
        }

        composable(BottomNavItem.Profile.route) {
            ProfileScreen(
                onNavigate = { navItem ->
                    navController.navigate(navItem.route) {
                        popUpTo(BottomNavItem.Home.route) {
                            saveState = true
                        }
                        launchSingleTop = true
                        restoreState = true
                    }
                }
            )
        }
    }
} 