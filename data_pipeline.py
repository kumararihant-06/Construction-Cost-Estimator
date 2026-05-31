import pandas as pd

# Store column names after encoding — needed for prediction alignment
FEATURE_COLUMNS = None

def load_and_process():
    global FEATURE_COLUMNS
    
    df = pd.read_csv('data/construction_data.csv')
    
    # Drop nulls
    df = df.dropna()
    
    # One-hot encode categorical columns
    # drop_first=True drops one category per feature to avoid multicollinearity
    # e.g. project_type: Residential/Commercial/Industrial → 2 binary columns
    df = pd.get_dummies(df, columns=['project_type', 'location_tier', 'material_grade'], 
                        drop_first=True)
    
    # Save feature columns (excluding target) for prediction alignment
    df = df.drop(columns=['labor_cost', 'material_cost'])
    FEATURE_COLUMNS = [col for col in df.columns if col != 'total_cost']
    
    return df

def get_feature_stats():
    df = pd.read_csv('data/construction_data.csv')
    stats = df[['size_sqft', 'duration_weeks', 'total_cost']].describe()
    return {
        'size_sqft': {
            'min': round(stats.loc['min', 'size_sqft'], 2),
            'max': round(stats.loc['max', 'size_sqft'], 2),
            'mean': round(stats.loc['mean', 'size_sqft'], 2)
        },
        'duration_weeks': {
            'min': round(stats.loc['min', 'duration_weeks'], 2),
            'max': round(stats.loc['max', 'duration_weeks'], 2),
            'mean': round(stats.loc['mean', 'duration_weeks'], 2)
        },
        'total_cost': {
            'min': round(stats.loc['min', 'total_cost'], 2),
            'max': round(stats.loc['max', 'total_cost'], 2),
            'mean': round(stats.loc['mean', 'total_cost'], 2)
        }
    }

if __name__ == '__main__':
    df = load_and_process()
    print(f"Shape: {df.shape}")
    print(df.head())
    print(f"\nFeature columns: {FEATURE_COLUMNS}")