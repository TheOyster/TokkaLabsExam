// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address owner) external view returns (uint256);
    function transfer(address to, uint256 value) external returns (bool);
    function transferFrom(address from, address to, uint256 value) external returns (bool);
}

interface IUniswapV2Router {
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
}

interface IUniswapV3Router {
    function exactInputSingle(
        address tokenIn,
        address tokenOut,
        uint24 fee,
        address recipient,
        uint deadline,
        uint amountIn,
        uint amountOutMinimum,
        uint160 sqrtPriceLimitX96
    ) external returns (uint amountOut);
}

interface ICurvePool {
    function exchange(
        int128 i,
        int128 j,
        uint256 dx,
        uint256 min_dy
    ) external;
}

contract TokenSwapper {
    IERC20 public immutable weth;
    IERC20 public immutable usdc;
    IERC20 public immutable usdt;
    IUniswapV2Router public immutable uniV2Router;
    IUniswapV3Router public immutable uniV3Router;
    ICurvePool public immutable curvePool;

    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the contract owner can call this function");
        _;
    }

    constructor(address _weth, address _usdc, address _usdt, address _uniV2Router, address _uniV3Router, address _curvePool) {
        weth = IERC20(_weth);
        usdc = IERC20(_usdc);
        usdt = IERC20(_usdt);
        uniV2Router = IUniswapV2Router(_uniV2Router);
        uniV3Router = IUniswapV3Router(_uniV3Router);
        curvePool = ICurvePool(_curvePool);
        owner = msg.sender;
    }

    function approveTokens(uint256 amountIn, uint256 x, uint256 y, uint256 z) external onlyOwner {
        require(x + y + z == 100, "Sum of x, y, z must be 100");

        uint256 wethForX = (amountIn * x) / 100;
        uint256 wethForY = (amountIn * y) / 100;
        uint256 wethForZ = (amountIn * z) / 100;

        // Approve WETH spending for Uniswap V2 and V3 routers, and Curve pool
        weth.approve(address(uniV2Router), wethForX + (wethForY / 2));
        weth.approve(address(uniV3Router), wethForY / 2);
        weth.approve(address(curvePool), wethForZ);
    }

    function swapWETH(uint256 amountIn, uint256 x, uint256 y, uint256 z, uint256 minOut) external onlyOwner {
        require(x + y + z == 100, "Sum of x, y, z must be 100");
        require(weth.balanceOf(address(this)) >= amountIn, "Insufficient WETH balance");

        uint256 wethForX = (amountIn * x) / 100;
        uint256 wethForY = (amountIn * y) / 100;
        uint256 wethForZ = (amountIn * z) / 100;

        // Swap on Uniswap V2 for x%
        _swapOnUniswapV2(wethForX, true);

        // Swap on Uniswap V2 and V3 for y%
        _swapOnUniswapV2(wethForY / 2, false);
        _swapOnUniswapV3(wethForY / 2, address(weth), address(usdt), 3000); // Specify the appropriate fee tier

        // Swap on Curve for z%
        curvePool.exchange(0, 2, wethForZ, 1); // Indices and min_dy should be set correctly

        // Check if the total USDT received meets the minimum output requirement
        uint256 totalUsdtReceived = usdt.balanceOf(address(this));
        require(totalUsdtReceived >= minOut, "Insufficient USDT received");
    }

    function _swapOnUniswapV2(uint256 amountIn, bool isUsdc) private {
        address[] memory path = new address[](2);
        path[0] = address(weth);
        path[1] = isUsdc ? address(usdc) : address(usdt);
        uniV2Router.swapExactTokensForTokens(amountIn, 0, path, address(this), block.timestamp + 300);
    }

    function _swapOnUniswapV3(uint256 amountIn, address tokenIn, address tokenOut, uint24 fee) private {
        uniV3Router.exactInputSingle(tokenIn, tokenOut, fee, address(this), block.timestamp + 300, amountIn, 0, 0);
    }

    function withdraw(address token, uint256 amount) external onlyOwner {
        require(IERC20(token).transfer(owner, amount), "Token transfer failed");
    }
}