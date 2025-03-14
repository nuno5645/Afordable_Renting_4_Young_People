package com.casaslisboa.ui.screens

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.casaslisboa.model.RentalProperty
import com.casaslisboa.ui.components.LisbonRentalsBottomNavigation
import com.casaslisboa.ui.components.LisbonRentalsTopAppBar
import com.casaslisboa.ui.components.PropertyCard
import com.casaslisboa.ui.components.BottomNavItem
import com.casaslisboa.ui.theme.LisbonRentalsTheme

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    properties: List<RentalProperty>,
    onFavoriteClick: (String) -> Unit,
    onEmailClick: (String) -> Unit,
    onDeleteClick: (String) -> Unit,
    onVisitClick: (String) -> Unit,
    onFilterClick: () -> Unit,
    onNavigate: (BottomNavItem) -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        topBar = {
            LisbonRentalsTopAppBar(
                title = "Lisbon Rentals",
                onFilterClick = onFilterClick,
                onSearchClick = { onNavigate(BottomNavItem.Search) }
            )
        },
        bottomBar = {
            LisbonRentalsBottomNavigation(
                currentRoute = BottomNavItem.Home.route,
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
            LazyColumn {
                items(properties) { property ->
                    PropertyCard(
                        property = property,
                        onFavoriteClick = onFavoriteClick,
                        onEmailClick = onEmailClick,
                        onDeleteClick = onDeleteClick,
                        onVisitClick = onVisitClick
                    )
                }
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
fun HomeScreenPreview() {
    val sampleProperties = listOf(
        RentalProperty(
            id = "1",
            address = "avenida Embaixador Augusto de Castro, 23, Figueirinha",
            price = 900,
            area = 65.0,
            bedrooms = 1,
            imageUrl = "",
            isFavorite = false
        ),
        RentalProperty(
            id = "2",
            address = "Rua das Flores, Lisboa",
            price = 1200,
            area = 75.0,
            bedrooms = 2,
            imageUrl = "",
            isFavorite = true
        )
    )
    
    LisbonRentalsTheme {
        HomeScreen(
            properties = sampleProperties,
            onFavoriteClick = {},
            onEmailClick = {},
            onDeleteClick = {},
            onVisitClick = {},
            onFilterClick = {},
            onNavigate = {}
        )
    }
} 