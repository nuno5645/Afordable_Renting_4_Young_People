package com.casaslisboa.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.casaslisboa.ui.components.BottomNavItem
import com.casaslisboa.ui.components.LisbonRentalsBottomNavigation
import com.casaslisboa.ui.components.LisbonRentalsTopAppBar
import com.casaslisboa.ui.theme.LisbonRentalsTheme
import com.casaslisboa.ui.theme.PriceGreen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StatisticsScreen(
    onNavigate: (BottomNavItem) -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        topBar = {
            LisbonRentalsTopAppBar(
                title = "Market Statistics",
                onFilterClick = {}
            )
        },
        bottomBar = {
            LisbonRentalsBottomNavigation(
                currentRoute = BottomNavI tem.Analytics.route,
                onNavigate = onNavigate
            )
        },
        modifier = modifier.fillMaxSize()
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState())
        ) {
            // Header
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(bottom = 24.dp)
            ) {
                Icon(
                    imageVector = Icons.Filled.Check,
                    contentDescription = "Statistics",
                    tint = PriceGreen,
                    modifier = Modifier.size(32.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "Lisbon Rental Market",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold
                )
            }
            
            // Average Price Card
            StatisticsCard(
                title = "Average Rental Price",
                value = "€950",
                description = "Per month for a 1-bedroom apartment",
                color = PriceGreen
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Price Range Card
            StatisticsCard(
                title = "Price Range",
                value = "€600 - €1,500",
                description = "For 1-bedroom apartments in Lisbon",
                color = Color(0xFF2196F3)
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Most Expensive Areas
            Text(
                text = "Most Expensive Areas",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(vertical = 8.dp)
            )
            
            AreaPriceItem(area = "Chiado", price = "€1,400")
            AreaPriceItem(area = "Príncipe Real", price = "€1,350")
            AreaPriceItem(area = "Avenida da Liberdade", price = "€1,300")
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Most Affordable Areas
            Text(
                text = "Most Affordable Areas",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(vertical = 8.dp)
            )
            
            AreaPriceItem(area = "Benfica", price = "€650")
            AreaPriceItem(area = "Marvila", price = "€700")
            AreaPriceItem(area = "Chelas", price = "€750")
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Market Trend
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                ) {
                    Text(
                        text = "Market Trend",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Text(
                        text = "Prices have increased by 8% in the last year",
                        style = MaterialTheme.typography.bodyMedium
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Simple bar chart representation
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(120.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.Bottom
                    ) {
                        BarChartItem(height = 0.6f, label = "Jan")
                        BarChartItem(height = 0.7f, label = "Feb")
                        BarChartItem(height = 0.65f, label = "Mar")
                        BarChartItem(height = 0.8f, label = "Apr")
                        BarChartItem(height = 0.85f, label = "May")
                        BarChartItem(height = 0.9f, label = "Jun")
                        BarChartItem(height = 0.95f, label = "Jul")
                        BarChartItem(height = 1f, label = "Aug")
                    }
                }
            }
        }
    }
}

@Composable
fun StatisticsCard(
    title: String,
    value: String,
    description: String,
    color: Color
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = value,
                style = MaterialTheme.typography.headlineMedium,
                color = color,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(4.dp))
            
            Text(
                text = description,
                style = MaterialTheme.typography.bodyMedium,
                color = Color.Gray
            )
        }
    }
}

@Composable
fun AreaPriceItem(area: String, price: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = area,
            style = MaterialTheme.typography.bodyMedium
        )
        Text(
            text = price,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Bold,
            color = PriceGreen
        )
    }
}

@Composable
fun BarChartItem(height: Float, label: String) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Box(
            modifier = Modifier
                .width(24.dp)
                .height((100 * height).dp)
                .clip(RoundedCornerShape(topStart = 4.dp, topEnd = 4.dp))
                .background(PriceGreen)
        )
        
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(top = 4.dp)
        )
    }
}

@Preview(showBackground = true)
@Composable
fun StatisticsScreenPreview() {
    LisbonRentalsTheme {
        StatisticsScreen(
            onNavigate = {}
        )
    }
} 