package com.casaslisboa.model

data class RentalProperty(
    val id: String,
    val address: String,
    val price: Int,
    val area: Double,
    val bedrooms: Int,
    val imageUrl: String,
    val isFavorite: Boolean = false,
    val realtor: String = "idealista"
) 