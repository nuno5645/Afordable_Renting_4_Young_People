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
import androidx.compose.material.icons.outlined.Email
import androidx.compose.material.icons.outlined.ExitToApp
import androidx.compose.material.icons.outlined.LocationOn
import androidx.compose.material.icons.outlined.MailOutline
import androidx.compose.material.icons.outlined.MoreVert
import androidx.compose.material.icons.outlined.Notifications
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.rememberScrollState

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
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
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
                    Icon(Icons.Default.Person, contentDescription = "Edit Profile")
                },
                trailingContent = {
                    Icon(Icons.Default.ArrowForward, contentDescription = "Navigate")
                }
            )
            
            ListItem(
                headlineContent = { Text("Notifications") },
                leadingContent = {
                    Icon(Icons.Default.Notifications, contentDescription = "Notifications")
                },
                trailingContent = {
                    Icon(Icons.Default.ArrowForward, contentDescription = "Navigate")
                }
            )
            
            ListItem(
                headlineContent = { Text("Privacy") },
                leadingContent = {
                    Icon(Icons.Default.Lock, contentDescription = "Privacy")
                },
                trailingContent = {
                    Icon(Icons.Default.ArrowForward, contentDescription = "Navigate")
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
                    Icon(Icons.Outlined.LocationOn, contentDescription = "Language")
                },
                trailingContent = {
                    Icon(Icons.Default.ArrowForward, contentDescription = "Navigate")
                }
            )
            
            ListItem(
                headlineContent = { Text("Dark Mode") },
                leadingContent = {
                    Icon(Icons.Outlined.Settings, contentDescription = "Dark Mode")
                },
                trailingContent = {
                    Icon(Icons.Default.ArrowForward, contentDescription = "Navigate")
                }
            )

            ListItem(
                headlineContent = { Text("Push Notifications") },
                leadingContent = {
                    Icon(Icons.Outlined.Notifications, contentDescription = "Push Notifications")
                },
                trailingContent = {
                    Icon(Icons.Default.ArrowForward, contentDescription = "Navigate")
                }
            )

            Spacer(modifier = Modifier.height(24.dp))

            // Support Section
            Text(
                text = "Support",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.align(Alignment.Start)
            )
            Spacer(modifier = Modifier.height(8.dp))

            ListItem(
                headlineContent = { Text("Help Center") },
                leadingContent = {
                    Icon(Icons.Outlined.MailOutline, contentDescription = "Help Center")
                },
                trailingContent = {
                    Icon(Icons.Default.ArrowForward, contentDescription = "Navigate")
                }
            )

            ListItem(
                headlineContent = { Text("Contact Us") },
                leadingContent = {
                    Icon(Icons.Outlined.Email, contentDescription = "Contact Us")
                },
                trailingContent = {
                    Icon(Icons.Default.ArrowForward, contentDescription = "Navigate")
                }
            )

            ListItem(
                headlineContent = { Text("Terms of Service") },
                leadingContent = {
                    Icon(Icons.Outlined.MoreVert, contentDescription = "Terms of Service")
                },
                trailingContent = {
                    Icon(Icons.Default.ArrowForward, contentDescription = "Navigate")
                }
            )

            Spacer(modifier = Modifier.height(24.dp))

            // Logout Button
            Button(
                onClick = { /* Handle logout */ },
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.error
                ),
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(
                    Icons.Outlined.ExitToApp,
                    contentDescription = "Logout",
                    modifier = Modifier.padding(end = 8.dp)
                )
                Text("Logout")
            }
        }
    }
} 