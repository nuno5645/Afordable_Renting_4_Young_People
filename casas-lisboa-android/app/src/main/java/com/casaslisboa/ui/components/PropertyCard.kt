package com.casaslisboa.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.FavoriteBorder
import androidx.compose.material.icons.outlined.Email
import androidx.compose.material.icons.outlined.Delete
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.casaslisboa.model.RentalProperty
import com.casaslisboa.ui.theme.DarkGray
import com.casaslisboa.ui.theme.PriceGreen
import com.casaslisboa.ui.theme.LisbonRentalsTheme
import coil.compose.AsyncImage

@Composable
fun PropertyCard(
    property: RentalProperty,
    onFavoriteClick: (String) -> Unit,
    onEmailClick: (String) -> Unit,
    onDeleteClick: (String) -> Unit,
    onVisitClick: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column {
            Box {
                // Property Image
                AsyncImage(
                    model = property.imageUrl,
                    contentDescription = "Property image",
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(180.dp),
                    contentScale = ContentScale.Crop
                )
                
                // Favorite Icon
                IconButton(
                    onClick = { onFavoriteClick(property.id) },
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .padding(8.dp)
                ) {
                    Icon(
                        imageVector = if (property.isFavorite) Icons.Filled.Favorite else Icons.Filled.FavoriteBorder,
                        contentDescription = "Favorite",
                        tint = Color.White
                    )
                }
                
                // Image Navigation Arrows
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .align(Alignment.Center),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    IconButton(onClick = { /* Previous image */ }) {
                        Icon(
                            painter = painterResource(android.R.drawable.ic_media_previous),
                            contentDescription = "Previous image",
                            tint = Color.White
                        )
                    }
                    IconButton(onClick = { /* Next image */ }) {
                        Icon(
                            painter = painterResource(android.R.drawable.ic_media_next),
                            contentDescription = "Next image",
                            tint = Color.White
                        )
                    }
                }
                
                // Image Counter
                Box(
                    modifier = Modifier
                        .align(Alignment.BottomCenter)
                        .padding(bottom = 8.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(Color.Black.copy(alpha = 0.6f))
                        .padding(horizontal = 8.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = "1/5",
                        color = Color.White,
                        fontSize = 12.sp
                    )
                }
            }
            
            // Property Info
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
            ) {
                // Info Icon
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.padding(bottom = 8.dp)
                ) {
                    Icon(
                        imageVector = Icons.Outlined.Home,
                        contentDescription = "Info",
                        tint = DarkGray,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = property.address,
                        style = MaterialTheme.typography.bodyMedium,
                        color = DarkGray,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis
                    )
                }
                
                // Price
                Text(
                    text = "€${property.price}/month",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = PriceGreen
                )
                
                // Property Details
                Row(
                    modifier = Modifier.padding(top = 8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Bedrooms
                    Icon(
                        painter = painterResource(android.R.drawable.ic_menu_myplaces),
                        contentDescription = "Bedrooms",
                        tint = DarkGray,
                        modifier = Modifier.size(16.dp)
                    )
                    Text(
                        text = "${property.bedrooms}",
                        style = MaterialTheme.typography.bodySmall,
                        color = DarkGray,
                        modifier = Modifier.padding(start = 4.dp, end = 16.dp)
                    )
                    
                    // Area
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "${property.area} m²",
                        style = MaterialTheme.typography.bodySmall,
                        color = DarkGray
                    )
                    
                    Spacer(modifier = Modifier.weight(1f))
                    
                    // Realtor
                    Text(
                        text = property.realtor,
                        style = MaterialTheme.typography.labelSmall,
                        color = Color.Gray
                    )
                }
            }
            
            // Action Buttons
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                // Visit Button
                Button(
                    onClick = { onVisitClick(property.id) },
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(containerColor = Color.White),
                    border = ButtonDefaults.outlinedButtonBorder
                ) {
                    Icon(
                        imageVector = Icons.Outlined.Search,
                        contentDescription = "Visit",
                        tint = DarkGray
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "Visit",
                        color = DarkGray
                    )
                }
                
                Spacer(modifier = Modifier.width(8.dp))
                
                // Email Button
                IconButton(
                    onClick = { onEmailClick(property.id) }
                ) {
                    Icon(
                        imageVector = Icons.Outlined.Email,
                        contentDescription = "Email",
                        tint = DarkGray
                    )
                }
                
                // Delete Button
                IconButton(
                    onClick = { onDeleteClick(property.id) }
                ) {
                    Icon(
                        imageVector = Icons.Outlined.Delete,
                        contentDescription = "Delete",
                        tint = DarkGray
                    )
                }
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
fun PropertyCardPreview() {
    LisbonRentalsTheme {
        PropertyCard(
            property = RentalProperty(
                id = "1",
                address = "avenida Embaixador Augusto de Castro, 23, Figueirinha - Augusto Castro, Oeiras e São Julião da Barra, Oeiras e São Julião da Barra - Paço de Arcos - Caxias",
                price = 900,
                area = 0.0,
                bedrooms = 0,
                imageUrl = "",
                isFavorite = false
            ),
            onFavoriteClick = {},
            onEmailClick = {},
            onDeleteClick = {},
            onVisitClick = {}
        )
    }
} 