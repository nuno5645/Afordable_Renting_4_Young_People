package com.casaslisboa

import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.tooling.preview.Preview
import com.casaslisboa.model.RentalProperty
import com.casaslisboa.ui.screens.HomeScreen
import com.casaslisboa.ui.theme.LisbonRentalsTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            LisbonRentalsApp()
        }
    }
}

@Composable
fun LisbonRentalsApp() {
    val context = LocalContext.current
    
    // Sample data
    val properties = remember {
        mutableStateListOf(
            RentalProperty(
                id = "1",
                address = "avenida Embaixador Augusto de Castro, 23, Figueirinha - Augusto Castro, Oeiras e São Julião da Barra, Oeiras e São Julião da Barra - Paço de Arcos - Caxias",
                price = 900,
                area = 0.0,
                bedrooms = 0,
                imageUrl = "https://picsum.photos/id/1/500/300",
                isFavorite = false
            ),
            RentalProperty(
                id = "2",
                address = "Rua das Flores, Lisboa",
                price = 1200,
                area = 75.0,
                bedrooms = 2,
                imageUrl = "https://picsum.photos/id/2/500/300",
                isFavorite = true
            )
        )
    }
    
    LisbonRentalsTheme {
        HomeScreen(
            properties = properties,
            onFavoriteClick = { id ->
                val index = properties.indexOfFirst { it.id == id }
                if (index != -1) {
                    val property = properties[index]
                    properties[index] = property.copy(isFavorite = !property.isFavorite)
                    Toast.makeText(
                        context,
                        if (properties[index].isFavorite) "Added to favorites" else "Removed from favorites",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            },
            onEmailClick = { id ->
                Toast.makeText(context, "Email about property $id", Toast.LENGTH_SHORT).show()
            },
            onDeleteClick = { id ->
                Toast.makeText(context, "Delete property $id", Toast.LENGTH_SHORT).show()
                properties.removeIf { it.id == id }
            },
            onVisitClick = { id ->
                Toast.makeText(context, "Schedule visit for property $id", Toast.LENGTH_SHORT).show()
            },
            onFilterClick = {
                Toast.makeText(context, "Open filters", Toast.LENGTH_SHORT).show()
            },
            onNavigate = { navItem ->
                Toast.makeText(context, "Navigate to ${navItem.label}", Toast.LENGTH_SHORT).show()
            }
        )
    }
}

@Preview(showBackground = true)
@Composable
fun LisbonRentalsAppPreview() {
    LisbonRentalsApp()
} 