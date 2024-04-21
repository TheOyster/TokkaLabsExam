from web3 import Web3

# Initialize a web3 connection to an Ethereum node
w3 = Web3(Web3.HTTPProvider('https://eth.api.onfinality.io/rpc?apikey=afcd9beb-6ae7-4ab5-80d8-a619cb75af22'))

# Uniswap V2 Contract Address and ABI

def simulate_uniswap_transaction(token_in_qty, token_in, reserves, fee_percent):
    """
    Simulate a Uniswap V2 swap transaction.
    
    Args:
    token_in_qty (float): Amount of the token being swapped into the pool.
    token_in (str): Address of the token being swapped into the pool.
    reserves (dict): A dictionary with reserves of the tokens in the pool {'token_address': reserve_amount}.
    fee_percent (float): Transaction fee percentage used by the pool.
    
    Returns:
    float: The amount of the token being received from the pool.
    """
    # Determine input and output reserves based on the token addresses
    if token_in == WETH:
        reserve_in = reserves[WETH]
        reserve_out = reserves[USDC]
    else:
        reserve_in = reserves[USDC]
        reserve_out = reserves[WETH]
    
    # Adjust input amount for the transaction fee
    input_amount_adjusted = token_in_qty * (1 - fee_percent)
    
    # Calculate output using the constant product formula
    output = reserve_out - (reserve_in * reserve_out / (reserve_in + input_amount_adjusted))
    
    return output

# Constants for token addresses
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

# Reserves from the blockchain query
reserves = {
    WETH: 15446.42814216754,  # WETH reserves
    USDC: 26853692.230452,     # USDC reserves in smaller units (need to adjust if decimals are not considered)
}

# Fee percent for Uniswap V2
fee_percent = 0.003  # 0.3%

# Amount of WETH being sold
weth_sold = 0.590938840873296854  # Amount from the transaction

# Simulate the transaction
usdc_bought = simulate_uniswap_transaction(weth_sold, WETH, reserves, fee_percent)
print(f"The simulated USDC received from selling {weth_sold} WETH: would be {usdc_bought:,.3f} USDC")
