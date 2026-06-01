CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS sectors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS stocks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  symbol TEXT NOT NULL UNIQUE,
  company_name TEXT,
  sector_id UUID REFERENCES sectors(id),
  market_cap_category TEXT CHECK (market_cap_category IN ('large', 'mid', 'small', 'micro') OR market_cap_category IS NULL),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS stock_prices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
  trade_date DATE NOT NULL,
  open NUMERIC(14, 4) NOT NULL,
  high NUMERIC(14, 4) NOT NULL,
  low NUMERIC(14, 4) NOT NULL,
  close NUMERIC(14, 4) NOT NULL,
  volume BIGINT NOT NULL,
  delivery_qty BIGINT NOT NULL,
  delivery_percent NUMERIC(7, 3) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(stock_id, trade_date)
);

CREATE TABLE IF NOT EXISTS analytics_snapshots (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
  trade_date DATE NOT NULL,
  delivery_ma_5 NUMERIC(18, 4),
  delivery_ma_10 NUMERIC(18, 4),
  delivery_ma_30 NUMERIC(18, 4),
  delivery_ma_60 NUMERIC(18, 4),
  delivery_ma_90 NUMERIC(18, 4),
  surge_1m NUMERIC(12, 4),
  surge_2m NUMERIC(12, 4),
  surge_3m NUMERIC(12, 4),
  surge_6m NUMERIC(12, 4),
  accumulation_score NUMERIC(6, 2) NOT NULL,
  breakout_score NUMERIC(6, 2) NOT NULL,
  relative_strength_score NUMERIC(6, 2),
  institutional_confidence NUMERIC(6, 2),
  swing_signal TEXT NOT NULL CHECK (swing_signal IN ('BUY', 'WATCH', 'SELL')),
  risk_rating TEXT NOT NULL CHECK (risk_rating IN ('Low', 'Medium', 'High')),
  potential_upside NUMERIC(7, 3),
  label TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(stock_id, trade_date)
);

CREATE TABLE IF NOT EXISTS uploads (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  file_name TEXT NOT NULL,
  rows_loaded INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL CHECK (status IN ('accepted', 'failed')),
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_stock_prices_date ON stock_prices(trade_date DESC);
CREATE INDEX IF NOT EXISTS idx_stock_prices_stock_date ON stock_prices(stock_id, trade_date DESC);
CREATE INDEX IF NOT EXISTS idx_snapshots_score ON analytics_snapshots(accumulation_score DESC, trade_date DESC);
