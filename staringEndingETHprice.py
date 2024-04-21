from web3 import Web3

# Ethereum node connection
w3 = Web3(Web3.HTTPProvider('https://eth.api.onfinality.io/rpc?apikey=afcd9beb-6ae7-4ab5-80d8-a619cb75af22'))

# Uniswap V3 Quoter Contract Address and ABI
quoter_address = '0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6'
quoter_abi = [
    {"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH9","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},
    {"inputs":[],"name":"WETH9","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint160","name":"sqrtPriceLimitX96","type":"uint160"}],"name":"quoteExactInputSingle","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}
]

# Setup the Quoter contract
quoter_contract = w3.eth.contract(address=quoter_address, abi=quoter_abi)

def get_usdc_from_eth(quoter_contract, eth_amount, token_in, token_out, fee, block_number):
    amount_in_wei = w3.to_wei(eth_amount, 'ether')
    amount_out = quoter_contract.functions.quoteExactInputSingle(
        w3.to_checksum_address(token_in),
        w3.to_checksum_address(token_out),
        fee,
        amount_in_wei,
        0
    ).call(block_identifier=block_number)
    return w3.from_wei(amount_out, 'mwei')  # Assuming USDC has 6 decimals

# Token addresses and fee tier
eth_address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'  # Wrapped Ether
usdc_address = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'  # USDC
fee_tier = 500

# Block numbers to query
block_numbers = [17618642, 17618742]

# Amount of ETH to convert
eth_amount = 1  # Example: 1 ETH

# Fetch and display the results for each block number
for block in block_numbers:
    usdc_output = get_usdc_from_eth(quoter_contract, eth_amount, eth_address, usdc_address, fee_tier, block)
    print(f"At block {block}, 1 ETH is approximately {usdc_output:.5f} USDC.")

