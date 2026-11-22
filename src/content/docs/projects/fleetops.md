---
title: FleetOps
description: Multi-organization fleet management platform — backend architecture, 100+ role-based REST endpoints, GPS telemetry on PostGIS, and Docker/GitHub Actions delivery.
---

## Overview

FleetOps is a multi-organization fleet management platform, built as my capstone project. Each organization manages its own vehicles, drivers, and records, so the backend has to keep that data separated per tenant while staying fast enough for live GPS data.

## My role

Backend Developer / DevOps Engineer, April 2026 – Present. I designed the backend architecture and system structure and owned the delivery pipeline; the rest of the team handled the frontend.

## What I built

- Over 100 role-based REST API endpoints in C#, ASP.NET Core, and EF Core.
- GPS telemetry processing on PostgreSQL/PostGIS, with batched ingestion, rate limiting, and idempotent uploads so retries do not duplicate points.
- Background workers for automated vehicle maintenance reminders and fuel-consumption anomaly detection.
- JWT authentication with refresh tokens, plus cloud-based image storage.
- Docker containerization and a GitHub Actions pipeline running xUnit tests and publishing images automatically.

## Stack

C# · ASP.NET Core · EF Core · PostgreSQL + PostGIS · Docker · GitHub Actions · xUnit
