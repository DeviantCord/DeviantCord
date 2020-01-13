--
-- PostgreSQL database dump
--

-- Dumped from database version 11.6 (Ubuntu 11.6-1.pgdg18.04+1)
-- Dumped by pg_dump version 11.6

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
-- Name: deviantcord; Type: SCHEMA; Schema: -; Owner: deviantcord
--

CREATE SCHEMA deviantcord;


ALTER SCHEMA deviantcord OWNER TO deviantcord;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: deviant_test; Type: TABLE; Schema: deviantcord; Owner: deviantcord
--

CREATE TABLE deviantcord.deviant_test (
    id integer,
    comment text
);


ALTER TABLE deviantcord.deviant_test OWNER TO deviantcord;

--
-- Name: deviation_data; Type: TABLE; Schema: deviantcord; Owner: deviantcord
--

CREATE TABLE deviantcord.deviation_data (
    artist text NOT NULL,
    folder_name text NOT NULL,
    folderid text NOT NULL,
    inverse_folder boolean NOT NULL,
    dc_uuid text NOT NULL,
    last_update timestamp without time zone,
    last_check timestamp without time zone NOT NULL,
    latest_img_urls text[] NOT NULL,
    latest_pp_url text,
    latest_deviation_url text,
    response text NOT NULL,
    mature boolean,
    last_urls text[],
    last_ids text[],
    last_hybrid_ids text[],
    hybrid boolean,
    given_offset integer,
    hybrid_urls text[],
    hybrid_img_urls text[]
);


ALTER TABLE deviantcord.deviation_data OWNER TO deviantcord;

--
-- Name: deviation_data_all; Type: TABLE; Schema: deviantcord; Owner: deviantcord
--

CREATE TABLE deviantcord.deviation_data_all (
    artist text NOT NULL,
    dc_uuid text NOT NULL,
    last_update timestamp without time zone,
    last_check timestamp without time zone NOT NULL,
    latest_img_urls text[] NOT NULL,
    latest_pp_url text NOT NULL,
    latest_deviation_url text,
    response text NOT NULL,
    mature boolean,
    last_urls text[],
    last_ids text[]
);


ALTER TABLE deviantcord.deviation_data_all OWNER TO deviantcord;

--
-- Name: deviation_data_test; Type: TABLE; Schema: deviantcord; Owner: deviantcord
--

CREATE TABLE deviantcord.deviation_data_test (
    artist text NOT NULL,
    folder_name text NOT NULL,
    folderid text,
    inverse_listener boolean,
    dc_uuid text,
    last_update timestamp without time zone,
    latest_img_url text,
    latest_pp_url text,
    latest_deviation_url text NOT NULL,
    response jsonb NOT NULL
);


ALTER TABLE deviantcord.deviation_data_test OWNER TO deviantcord;

--
-- Name: TABLE deviation_data_test; Type: COMMENT; Schema: deviantcord; Owner: deviantcord
--

COMMENT ON TABLE deviantcord.deviation_data_test IS 'Used for storing Deviation Data regarding deviations on DA';


--
-- Name: deviation_listeners; Type: TABLE; Schema: deviantcord; Owner: deviantcord
--

CREATE TABLE deviantcord.deviation_listeners (
    serverid bigint NOT NULL,
    artist text NOT NULL,
    folderid text NOT NULL,
    foldertype text NOT NULL,
    dc_uuid text NOT NULL,
    ping_role boolean DEFAULT false,
    roles double precision[],
    channelid bigint,
    created timestamp without time zone NOT NULL,
    last_update timestamp without time zone NOT NULL,
    hybrid boolean,
    inverse boolean,
    foldername text,
    last_ids text[],
    last_hybrids text[],
    mature boolean
);


ALTER TABLE deviantcord.deviation_listeners OWNER TO deviantcord;

--
-- Name: deviation_notifications; Type: TABLE; Schema: deviantcord; Owner: deviantcord
--

CREATE TABLE deviantcord.deviation_notifications (
    channelid bigint NOT NULL,
    artist text NOT NULL,
    foldername text NOT NULL,
    deviation_link text NOT NULL,
    img_url text NOT NULL,
    pp_url text NOT NULL,
    id integer NOT NULL,
    inverse boolean,
    notif_creation timestamp without time zone
);


ALTER TABLE deviantcord.deviation_notifications OWNER TO deviantcord;

--
-- Name: deviation_notifications_id_seq; Type: SEQUENCE; Schema: deviantcord; Owner: deviantcord
--

CREATE SEQUENCE deviantcord.deviation_notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE deviantcord.deviation_notifications_id_seq OWNER TO deviantcord;

--
-- Name: deviation_notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: deviantcord; Owner: deviantcord
--

ALTER SEQUENCE deviantcord.deviation_notifications_id_seq OWNED BY deviantcord.deviation_notifications.id;


--
-- Name: journal_data; Type: TABLE; Schema: deviantcord; Owner: deviantcord
--

CREATE TABLE deviantcord.journal_data (
    artist text NOT NULL,
    dc_uuid text,
    latest_title text,
    latest_url text,
    latest_excerpt text,
    last_ids text[],
    last_check timestamp without time zone,
    latest_update timestamp without time zone,
    latest_pp text,
    response jsonb,
    mature boolean
);


ALTER TABLE deviantcord.journal_data OWNER TO deviantcord;

--
-- Name: listeners; Type: TABLE; Schema: deviantcord; Owner: deviantcord
--

CREATE TABLE deviantcord.listeners (
    serverid double precision,
    artist text,
    folderid text,
    "folder-type" text,
    channelid double precision,
    "latest-update" timestamp without time zone,
    dc_uuid text
);


ALTER TABLE deviantcord.listeners OWNER TO deviantcord;

--
-- Name: server_config; Type: TABLE; Schema: deviantcord; Owner: deviantcord
--

CREATE TABLE deviantcord.server_config (
    serverid bigint,
    prefix text,
    errite_optout boolean,
    required_role bigint,
    updated timestamp without time zone DEFAULT now()
);


ALTER TABLE deviantcord.server_config OWNER TO deviantcord;

--
-- Name: status_data; Type: TABLE; Schema: deviantcord; Owner: deviantcord
--

CREATE TABLE deviantcord.status_data (
    artist text,
    dc_uuid text,
    last_statusid text[],
    last_items_urls text[],
    last_items_src_url text[],
    last_urls text[],
    last_body text,
    mature boolean,
    last_update timestamp without time zone,
    last_check timestamp without time zone,
    response jsonb
);


ALTER TABLE deviantcord.status_data OWNER TO deviantcord;

--
-- Name: test_exp; Type: TABLE; Schema: deviantcord; Owner: deviantcord
--

CREATE TABLE deviantcord.test_exp (
    column_1 integer
);


ALTER TABLE deviantcord.test_exp OWNER TO deviantcord;

--
-- Name: test_table; Type: TABLE; Schema: deviantcord; Owner: deviantcord
--

CREATE TABLE deviantcord.test_table (
    artist text,
    folder text
);


ALTER TABLE deviantcord.test_table OWNER TO deviantcord;

--
-- Name: deviation_notifications id; Type: DEFAULT; Schema: deviantcord; Owner: deviantcord
--

ALTER TABLE ONLY deviantcord.deviation_notifications ALTER COLUMN id SET DEFAULT nextval('deviantcord.deviation_notifications_id_seq'::regclass);


--
-- Data for Name: deviant_test; Type: TABLE DATA; Schema: deviantcord; Owner: deviantcord
--



--
-- Data for Name: deviation_data; Type: TABLE DATA; Schema: deviantcord; Owner: deviantcord
--



--
-- Data for Name: deviation_data_all; Type: TABLE DATA; Schema: deviantcord; Owner: deviantcord
--



--
-- Data for Name: deviation_data_test; Type: TABLE DATA; Schema: deviantcord; Owner: deviantcord
--



--
-- Data for Name: deviation_listeners; Type: TABLE DATA; Schema: deviantcord; Owner: deviantcord
--



--
-- Data for Name: deviation_notifications; Type: TABLE DATA; Schema: deviantcord; Owner: deviantcord
--



--
-- Data for Name: journal_data; Type: TABLE DATA; Schema: deviantcord; Owner: deviantcord
--



--
-- Data for Name: listeners; Type: TABLE DATA; Schema: deviantcord; Owner: deviantcord
--



--
-- Data for Name: server_config; Type: TABLE DATA; Schema: deviantcord; Owner: deviantcord
--



--
-- Data for Name: status_data; Type: TABLE DATA; Schema: deviantcord; Owner: deviantcord
--



--
-- Data for Name: test_exp; Type: TABLE DATA; Schema: deviantcord; Owner: deviantcord
--



--
-- Data for Name: test_table; Type: TABLE DATA; Schema: deviantcord; Owner: deviantcord
--



--
-- Name: deviation_notifications_id_seq; Type: SEQUENCE SET; Schema: deviantcord; Owner: deviantcord
--

SELECT pg_catalog.setval('deviantcord.deviation_notifications_id_seq', 1, true);


--
-- PostgreSQL database dump complete
--

