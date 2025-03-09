package com.casaslisboa.ui.components

import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.casaslisboa.ui.theme.LisbonRentalsTheme

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LisbonRentalsTopAppBar(
    title: String,
    onFilterClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    TopAppBar(
        title = {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = title,
                    fontSize = 22.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        },
        actions = {
            FilledTonalButton(
                onClick = onFilterClick
            ) {
                Icon(
                    imageVector = Icons.Default.MoreVert,
                    contentDescription = "Filters"
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text("Filters")
            }
        },
        modifier = modifier
    )
}

@Preview
@Composable
fun LisbonRentalsTopAppBarPreview() {
    LisbonRentalsTheme {
        LisbonRentalsTopAppBar(
            title = "Lisbon Rentals",
            onFilterClick = {}
        )
    }
} 