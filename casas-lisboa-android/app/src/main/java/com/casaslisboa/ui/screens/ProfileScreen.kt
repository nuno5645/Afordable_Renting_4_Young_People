package com.casaslisboa.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.casaslisboa.ui.components.BottomNavItem
import com.casaslisboa.ui.components.LisbonRentalsBottomNavigation

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    onNavigate: (BottomNavItem) -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Profile") }
            )
        },
        bottomBar = {
            LisbonRentalsBottomNavigation(
                currentRoute = BottomNavItem.Profile.route,
                onNavigate = onNavigate
            )
        },
        modifier = modifier.fillMaxSize()
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Profile Image and Name Section
            Icon(
                imageVector = Icons.Default.AccountCircle,
                contentDescription = "Profile Picture",
                modifier = Modifier.size(80.dp)
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "John Doe",
                style = MaterialTheme.typography.headlineSmall
            )
            Text(
                text = "john.doe@example.com",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Account Section
            Text(
                text = "Account",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.align(Alignment.Start)
            )
            Spacer(modifier = Modifier.height(8.dp))
            
            ListItem(
                headlineContent = { Text("Edit Profile") },
                leadingContent = {
                    Icon(Icons.Default.Edit, contentDescription = "Edit Profile")
                },
                trailingContent = {
                    Icon(Icons.Default.ChevronRight, contentDescription = "Navigate")
                }
            )
            
            ListItem(
                headlineContent = { Text("Notifications") },
                leadingContent = {
                    Icon(Icons.Default.Notifications, contentDescription = "Notifications")
                },
                trailingContent = {
                    Icon(Icons.Default.ChevronRight, contentDescription = "Navigate")
                }
            )
            
            ListItem(
                headlineContent = { Text("Privacy") },
                leadingContent = {
                    Icon(Icons.Default.Lock, contentDescription = "Privacy")
                },
                trailingContent = {
                    Icon(Icons.Default.ChevronRight, contentDescription = "Navigate")
                }
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Preferences Section
            Text(
                text = "Preferences",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.align(Alignment.Start)
            )
            Spacer(modifier = Modifier.height(8.dp))
            
            ListItem(
                headlineContent = { Text("Language") },
                leadingContent = {
                    Icon(Icons.Default.Language, contentDescription = "Language")
                },
                trailingContent = {
                    Icon(Icons.Default.ChevronRight, contentDescription = "Navigate")
                }
            )
            
            ListItem(
                headlineContent = { Text("Dark Mode") },
                leadingContent = {
                    Icon(Icons.Default.DarkMode, contentDescription = "Dark Mode")
                },
                trailingContent = {
                    Icon(Icons.Default.ChevronRight, contentDescription = "Navigate")
                }
            )
        }
    }
} 