--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4
-- Dumped by pg_dump version 16.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: deviantcord; Type: SCHEMA; Schema: -; Owner: prod_deviantcord
--

CREATE SCHEMA deviantcord;


ALTER SCHEMA deviantcord OWNER TO prod_deviantcord;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: deviation_data; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE TABLE deviantcord.deviation_data (
    rowid bigint NOT NULL,
    artist text,
    folder_name text,
    folderid text,
    inverse_folder boolean,
    dc_uuid text,
    last_update timestamp without time zone,
    last_check timestamp without time zone,
    latest_img_urls text[],
    latest_pp_url text,
    latest_deviation_url text,
    mature boolean,
    last_urls text[],
    last_ids text[],
    last_hybrid_ids text[],
    hybrid boolean,
    given_offset bigint,
    hybrid_urls text[],
    hybrid_img_urls text[],
    disabled boolean,
    shard_id bigint,
    isgroupuser boolean
);


ALTER TABLE deviantcord.deviation_data OWNER TO prod_deviantcord;

--
-- Name: TABLE deviation_data; Type: COMMENT; Schema: deviantcord; Owner: prod_deviantcord
--

COMMENT ON TABLE deviantcord.deviation_data IS 'Stores deviation tracking data including latest URLs and hybrid information';


--
-- Name: deviation_data_all; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE TABLE deviantcord.deviation_data_all (
    rowid bigint NOT NULL,
    artist text,
    dc_uuid text,
    last_update timestamp without time zone,
    last_check timestamp without time zone,
    latest_img_urls text[],
    latest_pp_url text,
    latest_deviation_url text,
    mature boolean,
    last_urls text[],
    last_ids text[],
    disabled boolean DEFAULT false,
    shard_id bigint,
    isgroupuser boolean
);


ALTER TABLE deviantcord.deviation_data_all OWNER TO prod_deviantcord;

--
-- Name: deviation_data_all_rowid_seq; Type: SEQUENCE; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE deviantcord.deviation_data_all ALTER COLUMN rowid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME deviantcord.deviation_data_all_rowid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: deviation_data_rowid_seq; Type: SEQUENCE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE SEQUENCE deviantcord.deviation_data_rowid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE deviantcord.deviation_data_rowid_seq OWNER TO prod_deviantcord;

--
-- Name: deviation_data_rowid_seq; Type: SEQUENCE OWNED BY; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER SEQUENCE deviantcord.deviation_data_rowid_seq OWNED BY deviantcord.deviation_data.rowid;


--
-- Name: deviation_listeners; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE TABLE deviantcord.deviation_listeners (
    serverid bigint,
    artist text,
    folderid text,
    foldertype text,
    dc_uuid text,
    ping_role boolean DEFAULT false,
    roles numeric(10,0)[],
    channelid bigint,
    created timestamp without time zone,
    last_update timestamp without time zone,
    hybrid boolean,
    inverse boolean,
    foldername text,
    last_ids text[],
    last_hybrids text[],
    mature boolean,
    disabled boolean DEFAULT false,
    shard_id bigint,
    rowid bigint NOT NULL
);


ALTER TABLE deviantcord.deviation_listeners OWNER TO prod_deviantcord;

--
-- Name: deviation_listeners_rowid_seq; Type: SEQUENCE; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE deviantcord.deviation_listeners ALTER COLUMN rowid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME deviantcord.deviation_listeners_rowid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: deviation_notifications; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE TABLE deviantcord.deviation_notifications (
    channelid bigint,
    artist text,
    foldername text,
    deviation_link text,
    img_url text,
    pp_url text,
    id bigint NOT NULL,
    inverse boolean,
    notif_creation timestamp without time zone,
    mature_only boolean,
    rowid bigint
);


ALTER TABLE deviantcord.deviation_notifications OWNER TO prod_deviantcord;

--
-- Name: deviation_notifications_id_seq; Type: SEQUENCE; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE deviantcord.deviation_notifications ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME deviantcord.deviation_notifications_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: journal_data; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE TABLE deviantcord.journal_data (
    artist text,
    dc_uuid text,
    latest_title text,
    latest_url text,
    latest_excerpt text,
    last_ids text[],
    last_check timestamp without time zone,
    latest_update timestamp without time zone,
    latest_pp text,
    mature boolean,
    thumb_img_url text,
    last_urls text[],
    last_excerpts text[],
    last_titles text[],
    rowid bigint NOT NULL,
    thumb_ids text[]
);


ALTER TABLE deviantcord.journal_data OWNER TO prod_deviantcord;

--
-- Name: journal_data_rowid_seq; Type: SEQUENCE; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE deviantcord.journal_data ALTER COLUMN rowid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME deviantcord.journal_data_rowid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: journal_listeners; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE TABLE deviantcord.journal_listeners (
    artist text,
    dc_uuid text,
    last_ids text[],
    last_check text,
    latest_update text,
    latest_pp text,
    mature boolean,
    serverid bigint,
    channelid bigint,
    rowid bigint NOT NULL
);


ALTER TABLE deviantcord.journal_listeners OWNER TO prod_deviantcord;

--
-- Name: journal_listeners_rowid_seq; Type: SEQUENCE; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE deviantcord.journal_listeners ALTER COLUMN rowid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME deviantcord.journal_listeners_rowid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: journal_notifications; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE TABLE deviantcord.journal_notifications (
    channelid bigint,
    artist text,
    pp_url text,
    title text,
    id bigint NOT NULL,
    url text,
    thumbnail text,
    notification_creation text,
    mature boolean,
    rowid bigint NOT NULL
);


ALTER TABLE deviantcord.journal_notifications OWNER TO prod_deviantcord;

--
-- Name: journal_notifications_id_seq; Type: SEQUENCE; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE deviantcord.journal_notifications ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME deviantcord.journal_notifications_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: journal_notifications_rowid_seq; Type: SEQUENCE; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE deviantcord.journal_notifications ALTER COLUMN rowid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME deviantcord.journal_notifications_rowid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: server_config; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE TABLE deviantcord.server_config (
    serverid bigint,
    prefix text,
    errite_optout boolean,
    required_role bigint,
    updated timestamp without time zone,
    server_language text,
    rowid bigint NOT NULL
);


ALTER TABLE deviantcord.server_config OWNER TO prod_deviantcord;

--
-- Name: server_config_rowid_seq; Type: SEQUENCE; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE deviantcord.server_config ALTER COLUMN rowid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME deviantcord.server_config_rowid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: status_data; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE TABLE deviantcord.status_data (
    artist text NOT NULL,
    dc_uuid text,
    last_statusid text[],
    last_items_urls text[],
    last_urls text[],
    last_bodys text[],
    last_update timestamp without time zone,
    last_check timestamp without time zone,
    last_pp text,
    thumb_ids text[]
);


ALTER TABLE deviantcord.status_data OWNER TO prod_deviantcord;

--
-- Name: status_listeners; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE TABLE deviantcord.status_listeners (
    id bigint NOT NULL,
    artist text,
    dc_uuid text,
    last_ids text[],
    last_check text,
    latest_update text,
    latest_pp text,
    serverid bigint,
    channelid bigint,
    rowid bigint NOT NULL
);


ALTER TABLE deviantcord.status_listeners OWNER TO prod_deviantcord;

--
-- Name: status_listeners_id_seq; Type: SEQUENCE; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE deviantcord.status_listeners ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME deviantcord.status_listeners_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: status_listeners_rowid_seq; Type: SEQUENCE; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE deviantcord.status_listeners ALTER COLUMN rowid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME deviantcord.status_listeners_rowid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: status_notifications; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE TABLE deviantcord.status_notifications (
    id bigint NOT NULL,
    notification_creation text,
    pp_url text,
    url text,
    body text,
    artist text,
    thumbnail text,
    channelid bigint,
    rowid bigint NOT NULL
);


ALTER TABLE deviantcord.status_notifications OWNER TO prod_deviantcord;

--
-- Name: status_notifications_id_seq; Type: SEQUENCE; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE deviantcord.status_notifications ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME deviantcord.status_notifications_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: status_notifications_rowid_seq; Type: SEQUENCE; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE deviantcord.status_notifications ALTER COLUMN rowid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME deviantcord.status_notifications_rowid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: deviation_data rowid; Type: DEFAULT; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE ONLY deviantcord.deviation_data ALTER COLUMN rowid SET DEFAULT nextval('deviantcord.deviation_data_rowid_seq'::regclass);


--
-- Data for Name: deviation_data; Type: TABLE DATA; Schema: deviantcord; Owner: prod_deviantcord
--



--
-- Data for Name: deviation_data_all; Type: TABLE DATA; Schema: deviantcord; Owner: prod_deviantcord
--



--
-- Data for Name: deviation_listeners; Type: TABLE DATA; Schema: deviantcord; Owner: prod_deviantcord
--



--
-- Data for Name: deviation_notifications; Type: TABLE DATA; Schema: deviantcord; Owner: prod_deviantcord
--



--
-- Data for Name: journal_data; Type: TABLE DATA; Schema: deviantcord; Owner: prod_deviantcord
--



--
-- Data for Name: journal_listeners; Type: TABLE DATA; Schema: deviantcord; Owner: prod_deviantcord
--



--
-- Data for Name: journal_notifications; Type: TABLE DATA; Schema: deviantcord; Owner: prod_deviantcord
--



--
-- Data for Name: server_config; Type: TABLE DATA; Schema: deviantcord; Owner: prod_deviantcord
--


--
-- Data for Name: status_data; Type: TABLE DATA; Schema: deviantcord; Owner: prod_deviantcord
--



--
-- Data for Name: status_listeners; Type: TABLE DATA; Schema: deviantcord; Owner: prod_deviantcord
--



--
-- Data for Name: status_notifications; Type: TABLE DATA; Schema: deviantcord; Owner: prod_deviantcord
--



--
-- Name: deviation_data_all_rowid_seq; Type: SEQUENCE SET; Schema: deviantcord; Owner: prod_deviantcord
--

SELECT pg_catalog.setval('deviantcord.deviation_data_all_rowid_seq', 6, true);


--
-- Name: deviation_data_rowid_seq; Type: SEQUENCE SET; Schema: deviantcord; Owner: prod_deviantcord
--

SELECT pg_catalog.setval('deviantcord.deviation_data_rowid_seq', 3, true);


--
-- Name: deviation_listeners_rowid_seq; Type: SEQUENCE SET; Schema: deviantcord; Owner: prod_deviantcord
--

SELECT pg_catalog.setval('deviantcord.deviation_listeners_rowid_seq', 13, true);


--
-- Name: deviation_notifications_id_seq; Type: SEQUENCE SET; Schema: deviantcord; Owner: prod_deviantcord
--

SELECT pg_catalog.setval('deviantcord.deviation_notifications_id_seq', 1, false);


--
-- Name: journal_data_rowid_seq; Type: SEQUENCE SET; Schema: deviantcord; Owner: prod_deviantcord
--

SELECT pg_catalog.setval('deviantcord.journal_data_rowid_seq', 6, true);


--
-- Name: journal_listeners_rowid_seq; Type: SEQUENCE SET; Schema: deviantcord; Owner: prod_deviantcord
--

SELECT pg_catalog.setval('deviantcord.journal_listeners_rowid_seq', 7, true);


--
-- Name: journal_notifications_id_seq; Type: SEQUENCE SET; Schema: deviantcord; Owner: prod_deviantcord
--

SELECT pg_catalog.setval('deviantcord.journal_notifications_id_seq', 1, false);


--
-- Name: journal_notifications_rowid_seq; Type: SEQUENCE SET; Schema: deviantcord; Owner: prod_deviantcord
--

SELECT pg_catalog.setval('deviantcord.journal_notifications_rowid_seq', 1, false);


--
-- Name: server_config_rowid_seq; Type: SEQUENCE SET; Schema: deviantcord; Owner: prod_deviantcord
--

SELECT pg_catalog.setval('deviantcord.server_config_rowid_seq', 2, true);


--
-- Name: status_listeners_id_seq; Type: SEQUENCE SET; Schema: deviantcord; Owner: prod_deviantcord
--

SELECT pg_catalog.setval('deviantcord.status_listeners_id_seq', 1, false);


--
-- Name: status_listeners_rowid_seq; Type: SEQUENCE SET; Schema: deviantcord; Owner: prod_deviantcord
--

SELECT pg_catalog.setval('deviantcord.status_listeners_rowid_seq', 1, false);


--
-- Name: status_notifications_id_seq; Type: SEQUENCE SET; Schema: deviantcord; Owner: prod_deviantcord
--

SELECT pg_catalog.setval('deviantcord.status_notifications_id_seq', 1, false);


--
-- Name: status_notifications_rowid_seq; Type: SEQUENCE SET; Schema: deviantcord; Owner: prod_deviantcord
--

SELECT pg_catalog.setval('deviantcord.status_notifications_rowid_seq', 1, false);


--
-- Name: deviation_data_all deviation_data_all_pkey; Type: CONSTRAINT; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE ONLY deviantcord.deviation_data_all
    ADD CONSTRAINT deviation_data_all_pkey PRIMARY KEY (rowid);


--
-- Name: deviation_data deviation_data_pkey; Type: CONSTRAINT; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE ONLY deviantcord.deviation_data
    ADD CONSTRAINT deviation_data_pkey PRIMARY KEY (rowid);


--
-- Name: deviation_listeners deviation_listeners_pkey; Type: CONSTRAINT; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE ONLY deviantcord.deviation_listeners
    ADD CONSTRAINT deviation_listeners_pkey PRIMARY KEY (rowid);


--
-- Name: deviation_notifications deviation_notifications_pkey; Type: CONSTRAINT; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE ONLY deviantcord.deviation_notifications
    ADD CONSTRAINT deviation_notifications_pkey PRIMARY KEY (id);


--
-- Name: journal_data journal_data_pkey; Type: CONSTRAINT; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE ONLY deviantcord.journal_data
    ADD CONSTRAINT journal_data_pkey PRIMARY KEY (rowid);


--
-- Name: journal_listeners journal_listeners_pkey; Type: CONSTRAINT; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE ONLY deviantcord.journal_listeners
    ADD CONSTRAINT journal_listeners_pkey PRIMARY KEY (rowid);


--
-- Name: journal_notifications journal_notifications_pkey; Type: CONSTRAINT; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE ONLY deviantcord.journal_notifications
    ADD CONSTRAINT journal_notifications_pkey PRIMARY KEY (rowid);


--
-- Name: server_config server_config_pkey; Type: CONSTRAINT; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE ONLY deviantcord.server_config
    ADD CONSTRAINT server_config_pkey PRIMARY KEY (rowid);


--
-- Name: status_data status_data_pkey; Type: CONSTRAINT; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE ONLY deviantcord.status_data
    ADD CONSTRAINT status_data_pkey PRIMARY KEY (artist);


--
-- Name: status_listeners status_listeners_pkey; Type: CONSTRAINT; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE ONLY deviantcord.status_listeners
    ADD CONSTRAINT status_listeners_pkey PRIMARY KEY (id);


--
-- Name: status_notifications status_notifications_pkey; Type: CONSTRAINT; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE ONLY deviantcord.status_notifications
    ADD CONSTRAINT status_notifications_pkey PRIMARY KEY (id);


--
-- Name: idx_deviation_data_artist; Type: INDEX; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE INDEX idx_deviation_data_artist ON deviantcord.deviation_data USING btree (artist);


--
-- Name: idx_deviation_data_folderid; Type: INDEX; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE INDEX idx_deviation_data_folderid ON deviantcord.deviation_data USING btree (folderid);


--
-- Name: idx_deviation_data_last_update; Type: INDEX; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE INDEX idx_deviation_data_last_update ON deviantcord.deviation_data USING btree (last_update);


--
-- Name: idx_deviation_data_shard_id; Type: INDEX; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE INDEX idx_deviation_data_shard_id ON deviantcord.deviation_data USING btree (shard_id);


--
-- PostgreSQL database dump complete
--

