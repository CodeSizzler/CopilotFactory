"""
Salem Hotel Agent - A simple agent with a tool to find hotels in Salem.
Uses Microsoft Agent Framework with Azure AI Foundry.
Ready for deployment to Foundry Hosted Agent service.
"""

import asyncio
import os
from typing import Annotated
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

from agent_framework.azure import AzureAIAgentClient
from azure.ai.agentserver.agentframework import from_agent_framework
from azure.identity.aio import DefaultAzureCredential

# Configure these for your Foundry project via environment variables (see .env.sample)
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

if not PROJECT_ENDPOINT:
    raise SystemExit(
        "Error: PROJECT_ENDPOINT environment variable is not set.\n"
        "Copy .env.sample to .env and fill in your Azure AI Foundry project endpoint."
    )


# Simulated hotel data for Salem
SALEM_HOTELS = [
    {"name": "Radisson Hotel Salem", "price_per_night": 189, "rating": 4.5, "location": "Salem Steel Plant"},
    {"name": "Zibe Salem by GRT Hotels", "price_per_night": 159, "rating": 4.2, "location": "Salem 4 Roads"},
    {"name": "Grand Estancia", "price_per_night": 249, "rating": 4.7, "location": "Salem Bangalore Highway"},
    {"name": "CJ Palazzio", "price_per_night": 219, "rating": 4.4, "location": "Salem AVR Round Exit"},
    {"name": "Sivaraj Inn", "price_per_night": 139, "rating": 4.0, "location": "Opp to Sona College Salem"},
    {"name": "Hotel Cenneys Gateway", "price_per_night": 99, "rating": 3.8, "location": "Sarada College Road Salem"},
]


def get_available_hotels(
    check_in_date: Annotated[str, "Check-in date in YYYY-MM-DD format"],
    check_out_date: Annotated[str, "Check-out date in YYYY-MM-DD format"],
    max_price: Annotated[int, "Maximum price per night in USD (optional)"] = 500,
) -> str:
    """
    Get available hotels in Salem for the specified dates.
    This simulates a call to a fake hotel availability API.
    """
    try:
        # Parse dates
        check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
        check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
        
        # Validate dates
        if check_out <= check_in:
            return "Error: Check-out date must be after check-in date."
        
        nights = (check_out - check_in).days
        
        # Filter hotels by price
        available_hotels = [
            hotel for hotel in SALEM_HOTELS 
            if hotel["price_per_night"] <= max_price
        ]
        
        if not available_hotels:
            return f"No hotels found in Salem within your budget of ${max_price}/night."
        
        # Build response
        result = f"Available hotels in Salem from {check_in_date} to {check_out_date} ({nights} nights):\n\n"
        
        for hotel in available_hotels:
            total_cost = hotel["price_per_night"] * nights
            result += f"**{hotel['name']}**\n"
            result += f"   Location: {hotel['location']}\n"
            result += f"   Rating: {hotel['rating']}/5\n"
            result += f"   ${hotel['price_per_night']}/night (Total: ${total_cost})\n\n"
        
        return result
        
    except ValueError as e:
        return f"Error parsing dates. Please use YYYY-MM-DD format. Details: {str(e)}"


async def main():
    """Main function to run the agent as a web server."""
    async with (
        DefaultAzureCredential() as credential,
        AzureAIAgentClient(
            project_endpoint=PROJECT_ENDPOINT,
            model_deployment_name=MODEL_DEPLOYMENT_NAME,
            credential=credential,
        ) as client,
    ):
        agent = client.create_agent(
            name="SalemHotelAgent",
            instructions="""You are a helpful travel assistant specializing in finding hotels in Salem, Washington.

When a user asks about hotels in Salem:
1. Ask for their check-in and check-out dates if not provided
2. Ask about their budget preferences if not mentioned
3. Use the get_available_hotels tool to find available options
4. Present the results in a friendly, informative way
5. Offer to help with additional questions about the hotels or Salem

Be conversational and helpful. If users ask about things outside of Salem hotels, 
politely let them know you specialize in Salem hotel recommendations.""",
            tools=[get_available_hotels],
        )

        print("Salem Hotel Agent Server running on http://localhost:8088")
        server = from_agent_framework(agent)
        await server.run_async()


if __name__ == "__main__":
    asyncio.run(main())
