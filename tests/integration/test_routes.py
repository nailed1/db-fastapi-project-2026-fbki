"""Smoke tests for FastAPI routes (require running DB)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_index(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    assert "HotelBook" in response.text


@pytest.mark.asyncio
async def test_bookings_list(client: AsyncClient) -> None:
    response = await client.get("/bookings/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_guests_list(client: AsyncClient) -> None:
    response = await client.get("/guests/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_rooms_list(client: AsyncClient) -> None:
    response = await client.get("/rooms/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_manager_dashboard(client: AsyncClient) -> None:
    response = await client.get("/manager/dashboard")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_available_rooms_missing_params(client: AsyncClient) -> None:
    response = await client.get("/bookings/available-rooms")
    assert response.status_code == 422  # missing required query params
