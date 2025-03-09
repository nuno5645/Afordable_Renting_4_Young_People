package com.casaslisboa.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.FavoriteBorder
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.casaslisboa.model.RentalProperty
import com.casaslisboa.ui.components.BottomNavItem
import com.casaslisboa.ui.components.LisbonRentalsBottomNavigation
import com.casaslisboa.ui.components.LisbonRentalsTopAppBar
import com.casaslisboa.ui.components.PropertyCard
import com.casaslisboa.ui.theme.LisbonRentalsTheme

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FavoritesScreen(
    favoriteProperties: List<RentalProperty>,
    onFavoriteClick: (String) -> Unit,
    onEmailClick: (String) -> Unit,
    onDeleteClick: (String) -> Unit,
    onVisitClick: (String) -> Unit,
    onNavigate: (BottomNavItem) -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        topBar = {
            LisbonRentalsTopAppBar(
                title = "Favorites",
                onFilterClick = {}
            )
        },
        bottomBar = {
            LisbonRentalsBottomNavigation(
                currentRoute = BottomNavItem.Favorites.route,
                onNavigate = onNavigate
            )
        },
        modifier = modifier.fillMaxSize()
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            if (favoriteProperties.isEmpty()) {
                // Empty state
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Icon(
                        imageVector = Icons.Outlined.FavoriteBorder,
                        contentDescription = "No favorites",
                        modifier = Modifier.size(80.dp),
                        tint = Color.Gray
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "No Favorites Yet",
                        style = MaterialTheme.typography.headlineMedium,
                        color = Color.White
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Properties you favorite will appear here",
                        style = MaterialTheme.typography.bodyMedium,
                        color = Color.Gray,
                        textAlign = TextAlign.Center
                    )
                }
            } else {
                // List of favorite properties
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp)
                ) {
                    Text(
                        text = "Your Favorite Properties",
                        style = MaterialTheme.typography.titleLarge,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                    
                    // List of favorite properties
                    Column {
                        favoriteProperties.forEach { property ->
                            PropertyCard(
                                property = property,
                                onFavoriteClick = onFavoriteClick,
                                onEmailClick = onEmailClick,
                                onDeleteClick = onDeleteClick,
                                onVisitClick = onVisitClick
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                        }
                    }
                }
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
fun FavoritesScreenPreview() {
    LisbonRentalsTheme {
        FavoritesScreen(
            favoriteProperties = emptyList(),
            onFavoriteClick = {},
            onEmailClick = {},
            onDeleteClick = {},
            onVisitClick = {},
            onNavigate = {}
        )
    }
} 