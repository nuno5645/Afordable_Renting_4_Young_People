"""
Simple LightGBM Example for House Price Prediction in Lisbon
This script trains a LightGBM model to predict house rental prices
using data from the houses table in SQLite database.
"""

import sqlite3
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import re


def extract_bedrooms(bedroom_str):
    """Extract number of bedrooms from string like 'T2', 'T3', etc."""
    if pd.isna(bedroom_str):
        return 0
    match = re.search(r'(\d+)', str(bedroom_str))
    if match:
        return int(match.group(1))
    return 0


def extract_floor(floor_str):
    """Extract floor number from string."""
    if pd.isna(floor_str):
        return 0
    match = re.search(r'(\d+)', str(floor_str))
    if match:
        return int(match.group(1))
    return 0


def extract_property_type(name):
    """Extract property type from name: apartamento vs moradia (house)"""
    if pd.isna(name):
        return 'other'
    name_lower = str(name).lower()
    if 'moradia' in name_lower or 'vivenda' in name_lower:
        return 'house'
    elif 'apartamento' in name_lower:
        return 'apartment'
    else:
        return 'other'


def load_data(db_path, district_id=22):
    """
    Load house data from SQLite database for a specific district.
    
    Args:
        db_path: Path to the SQLite database file
        district_id: ID of the district (22 for Lisbon)
    
    Returns:
        DataFrame with house data
    """
    conn = sqlite3.connect(db_path)
    
    # Query to get houses with related location information
    query = f"""
    SELECT 
        h.id,
        h.name,
        h.zone,
        h.price,
        h.bedrooms,
        h.area,
        h.floor,
        h.listing_type,
        h.source,
        h.county_id,
        h.district_id,
        h.parish_id,
        c.name as county_name,
        d.name as district_name,
        p.name as parish_name
    FROM houses h
    LEFT JOIN counties c ON h.county_id = c.id
    LEFT JOIN districts d ON h.district_id = d.id
    LEFT JOIN parishes p ON h.parish_id = p.id
    WHERE h.district_id = {district_id}
        AND h.listing_type = 'buy'
        AND h.price > 0
        AND h.area > 0
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df


def preprocess_data(df):
    """
    Preprocess the data for machine learning.
    
    Args:
        df: Raw DataFrame from database
    
    Returns:
        Processed DataFrame ready for training
    """
    # Create a copy to avoid modifying original
    data = df.copy()
    
    # Store original categorical columns before encoding
    data['source_original'] = data['source']
    data['county_name_original'] = data['county_name'] if 'county_name' in data.columns else None
    data['parish_name_original'] = data['parish_name'] if 'parish_name' in data.columns else None
    
    # Extract property type from name
    data['property_type'] = data['name'].apply(extract_property_type)
    
    # Extract numeric features
    data['bedrooms_num'] = data['bedrooms'].apply(extract_bedrooms)
    data['floor_num'] = data['floor'].apply(extract_floor)
    
    # Convert area to float
    data['area'] = pd.to_numeric(data['area'], errors='coerce')
    data['price'] = pd.to_numeric(data['price'], errors='coerce')
    
    # Calculate price per square meter
    data['price_per_sqm'] = data['price'] / data['area']
    
    # One-hot encode categorical features
    data = pd.get_dummies(data, columns=['source'], prefix='source')
    data = pd.get_dummies(data, columns=['property_type'], prefix='type')
    
    # Handle county encoding (one-hot)
    if 'county_name' in data.columns:
        data = pd.get_dummies(data, columns=['county_name'], prefix='county')
    
    # Handle parish encoding (one-hot) - using parish_id for better granularity
    if 'parish_id' in data.columns:
        # Create dummy variables for parish_id
        data['parish_id'] = data['parish_id'].fillna(0).astype(int)
        # Only create dummies if there are parishes
        if data['parish_id'].nunique() > 1:
            parish_dummies = pd.get_dummies(data['parish_id'], prefix='parish')
            data = pd.concat([data, parish_dummies], axis=1)
    
    # Remove rows with missing critical values
    data = data.dropna(subset=['price', 'area', 'bedrooms_num'])
    
    # Remove outliers (prices beyond reasonable range)
    # Different ranges for buying vs renting
    if 'listing_type' in data.columns and data['listing_type'].iloc[0] == 'buy':
        # For buying: remove extreme outliers
        data = data[(data['price'] >= 50000) & (data['price'] <= 2000000)]
    else:
        # For renting
        data = data[(data['price'] >= 200) & (data['price'] <= 5000)]
    
    # Remove unrealistic areas
    data = data[(data['area'] >= 10) & (data['area'] <= 500)]
    
    return data


def train_lightgbm_model(df):
    """
    Train a LightGBM model to predict house prices.
    
    Args:
        df: Preprocessed DataFrame
    
    Returns:
        Trained model, test data, predictions, and feature importance
    """
    # Select features for training (exclude _original columns and string columns used only for display)
    exclude_cols = ['id', 'name', 'zone', 'price', 'bedrooms', 'floor', 'listing_type', 
                    'county_id', 'district_id', 'parish_id', 'county_name', 'district_name', 
                    'parish_name', 'price_per_sqm', 'source_original', 'county_name_original', 
                    'parish_name_original']
    feature_cols = [col for col in df.columns if (col.startswith('source_') or 
                    col.startswith('county_') or
                    col.startswith('parish_') or
                    col.startswith('type_') or
                    col in ['bedrooms_num', 'area', 'floor_num']) and 
                    col not in exclude_cols and
                    not col.endswith('_original')]
    
    X = df[feature_cols]
    y = df['price']
    
    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\n{'='*60}")
    print(f"Dataset Information:")
    print(f"{'='*60}")
    print(f"Total samples: {len(df)}")
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    print(f"Number of features: {len(feature_cols)}")
    print(f"\nFeatures used: {feature_cols[:5]}{'...' if len(feature_cols) > 5 else ''}")
    
    # Create LightGBM datasets
    train_data = lgb.Dataset(X_train, label=y_train)
    test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
    
    # Set parameters
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'learning_rate': 0.05,
        'feature_fraction': 0.9,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': -1
    }
    
    # Train the model
    print(f"\n{'='*60}")
    print("Training LightGBM model...")
    print(f"{'='*60}")
    
    model = lgb.train(
        params,
        train_data,
        num_boost_round=200,
        valid_sets=[test_data],
        callbacks=[lgb.early_stopping(stopping_rounds=10)]
    )
    
    # Make predictions
    y_pred = model.predict(X_test, num_iteration=model.best_iteration)
    
    # Calculate metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"\n{'='*60}")
    print("Model Performance Metrics:")
    print(f"{'='*60}")
    print(f"Mean Absolute Error (MAE): €{mae:.2f}")
    print(f"Root Mean Squared Error (RMSE): €{rmse:.2f}")
    print(f"R² Score: {r2:.4f}")
    
    # Feature importance
    importance = model.feature_importance(importance_type='gain')
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': importance
    }).sort_values('importance', ascending=False)
    
    print(f"\n{'='*60}")
    print("Top 10 Most Important Features:")
    print(f"{'='*60}")
    print(feature_importance.head(10).to_string(index=False))
    
    # Show some prediction examples
    print(f"\n{'='*60}")
    print("Sample Predictions (first 10 test samples):")
    print(f"{'='*60}")
    comparison = pd.DataFrame({
        'Actual Price (€)': y_test.values[:10],
        'Predicted Price (€)': y_pred[:10],
        'Difference (€)': y_test.values[:10] - y_pred[:10]
    })
    print(comparison.to_string(index=False))
    
    # Return both the model results and the original dataframe indices for detailed analysis
    return model, X_test, y_test, y_pred, feature_importance, df


def analyze_data(df):
    """Print basic statistics about the dataset."""
    print(f"\n{'='*60}")
    print("Data Analysis Summary:")
    print(f"{'='*60}")
    
    print(f"\nPrice Statistics:")
    print(f"  Mean: €{df['price'].mean():.2f}")
    print(f"  Median: €{df['price'].median():.2f}")
    print(f"  Min: €{df['price'].min():.2f}")
    print(f"  Max: €{df['price'].max():.2f}")
    print(f"  Std Dev: €{df['price'].std():.2f}")
    
    print(f"\nArea Statistics (m²):")
    print(f"  Mean: {df['area'].mean():.2f}")
    print(f"  Median: {df['area'].median():.2f}")
    print(f"  Min: {df['area'].min():.2f}")
    print(f"  Max: {df['area'].max():.2f}")
    
    print(f"\nBedrooms Distribution:")
    bedrooms_count = df['bedrooms'].value_counts().head(5)
    for bedroom, count in bedrooms_count.items():
        print(f"  {bedroom}: {count} houses")
    
    if 'source' in df.columns:
        print(f"\nData Sources:")
        source_count = df['source'].value_counts()
        for source, count in source_count.items():
            print(f"  {source}: {count} houses")
    
    if 'county_name' in df.columns:
        print(f"\nTop 5 Counties by Number of Houses:")
        county_count = df['county_name'].value_counts().head(5)
        for county, count in county_count.items():
            print(f"  {county}: {count} houses")


def main():
    """Main function to run the LightGBM example."""
    # Database path (adjust if needed)
    db_path = '/home/hugoa/repos/Afordable_Renting_4_Young_People/django_api/api/db.sqlite3'
    
    print("="*60)
    print("LightGBM House Price Prediction - Lisbon District")
    print("="*60)
    
    # Load data
    print("\nLoading data from database...")
    df = load_data(db_path, district_id=22)
    print(f"Loaded {len(df)} houses from Lisbon district")
    
    if len(df) < 10:
        print("\nError: Not enough data to train a model!")
        print("Please ensure there are houses in district 22 (Lisbon) in the database.")
        return
    
    # Analyze raw data
    analyze_data(df)
    
    # Preprocess data
    print("\nPreprocessing data...")
    df_processed = preprocess_data(df)
    print(f"After preprocessing: {len(df_processed)} houses remain")
    
    if len(df_processed) < 10:
        print("\nError: Not enough data after preprocessing!")
        return
    
    # Train model
    model, X_test, y_test, y_pred, feature_importance, df_processed = train_lightgbm_model(df_processed)
    
    # Detailed predictions for specific house IDs
    print(f"\n{'='*60}")
    print("DETAILED PREDICTIONS FOR SPECIFIC HOUSES:")
    print(f"{'='*60}")
    
    # Get the indices from the test set
    test_indices = X_test.index
    
    # Create full predictions for all data (exclude _original columns and string columns)
    exclude_cols = ['id', 'name', 'zone', 'price', 'bedrooms', 'floor', 'listing_type', 
                    'county_id', 'district_id', 'parish_id', 'county_name', 'district_name', 
                    'parish_name', 'price_per_sqm', 'source_original', 'county_name_original', 
                    'parish_name_original', 'predicted_price', 'price_difference', 'price_difference_pct']
    all_features = [col for col in df_processed.columns if (col.startswith('source_') or 
                    col.startswith('county_') or
                    col.startswith('parish_') or
                    col.startswith('type_') or
                    col in ['bedrooms_num', 'area', 'floor_num']) and 
                    col not in exclude_cols and
                    not col.endswith('_original')]
    X_all = df_processed[all_features]
    all_predictions = model.predict(X_all, num_iteration=model.best_iteration)
    
    # Add predictions to the dataframe
    df_processed['predicted_price'] = all_predictions
    df_processed['price_difference'] = df_processed['price'] - df_processed['predicted_price']
    df_processed['price_difference_pct'] = (df_processed['price_difference'] / df_processed['price']) * 100
    
    # Specific house IDs to analyze (from your examples)
    specific_ids = [513, 517, 518, 519, 520, 521]
    
    print("\nSearching for specific houses from your examples:\n")
    
    for house_id in specific_ids:
        if house_id in df_processed.index:
            house = df_processed.loc[house_id]
            print(f"House ID: {house_id}")
            print(f"Name: {house['name'][:60]}...")
            print(f"Zone: {house['zone']}")
            print(f"Bedrooms: {house['bedrooms']} (numeric: {house['bedrooms_num']})")
            print(f"Area: {house['area']:.2f} m²")
            print(f"Floor: {house['floor']} (numeric: {house['floor_num']})")
            print(f"Source: {house['source_original']}")
            print(f"County: {house.get('county_name_original', 'N/A')}")
            print(f"\n  💰 ACTUAL PRICE:     €{house['price']:,.2f}")
            print(f"  🤖 PREDICTED PRICE:  €{house['predicted_price']:,.2f}")
            print(f"  📊 DIFFERENCE:       €{house['price_difference']:,.2f} ({house['price_difference_pct']:.1f}%)")
            
            diff_pct = abs(house['price_difference_pct'])
            if diff_pct < 10:
                print(f"  ✅ Prediction quality: EXCELLENT (within 10%)")
            elif diff_pct < 20:
                print(f"  ✔️  Prediction quality: GOOD (within 20%)")
            else:
                print(f"  ⚠️  Prediction quality: NEEDS IMPROVEMENT (over 20% difference)")
            
            print(f"{'-'*60}\n")
        else:
            print(f"House ID {house_id} not found in the processed dataset")
            print(f"{'-'*60}\n")
    
    # Show some random examples from test set
    print(f"\n{'='*60}")
    print("RANDOM EXAMPLES FROM TEST SET:")
    print(f"{'='*60}\n")
    
    sample_size = min(5, len(test_indices))
    sample_indices = test_indices[:sample_size]
    
    for idx in sample_indices:
        house = df_processed.loc[idx]
        print(f"House ID: {idx}")
        print(f"Name: {house['name'][:60]}...")
        print(f"Bedrooms: {house['bedrooms']} | Area: {house['area']:.0f}m² | Floor: {house['floor']}")
        print(f"  💰 ACTUAL:    €{house['price']:,.2f}")
        print(f"  🤖 PREDICTED: €{house['predicted_price']:,.2f}")
        print(f"  📊 DIFF:      €{house['price_difference']:,.2f} ({house['price_difference_pct']:.1f}%)")
        print(f"{'-'*60}\n")
    
    print(f"\n{'='*60}")
    print("Training completed successfully!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        traceback.print_exc()
