--
-- PostgreSQL database dump
--

-- Dumped from database version 12.8
-- Dumped by pg_dump version 12.8

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
-- Name: deviant_accounts; Type: TABLE; Schema: deviantcord; Owner: doadmin
--

CREATE TABLE deviantcord.deviant_accounts (
    username text,
    password text
);


ALTER TABLE deviantcord.deviant_accounts OWNER TO doadmin;

--
-- Name: deviant_test; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE TABLE deviantcord.deviant_test (
    id integer,
    comment text
);


ALTER TABLE deviantcord.deviant_test OWNER TO prod_deviantcord;

--
-- Name: deviation_data; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
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
    hybrid_img_urls text[],
    disabled boolean DEFAULT false,
    shard_id integer
);


ALTER TABLE deviantcord.deviation_data OWNER TO prod_deviantcord;

--
-- Name: deviation_data_all; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
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
    last_ids text[],
    disabled boolean DEFAULT false,
    shard_id integer
);


ALTER TABLE deviantcord.deviation_data_all OWNER TO prod_deviantcord;

--
-- Name: deviation_data_test; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
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


ALTER TABLE deviantcord.deviation_data_test OWNER TO prod_deviantcord;

--
-- Name: TABLE deviation_data_test; Type: COMMENT; Schema: deviantcord; Owner: prod_deviantcord
--

COMMENT ON TABLE deviantcord.deviation_data_test IS 'Used for storing Deviation Data regarding deviations on DA';


--
-- Name: deviation_listeners; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
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
    mature boolean,
    disabled boolean DEFAULT false,
    shard_id integer
);


ALTER TABLE deviantcord.deviation_listeners OWNER TO prod_deviantcord;

--
-- Name: deviation_notifications; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
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
    notif_creation timestamp without time zone,
    mature_only boolean
);


ALTER TABLE deviantcord.deviation_notifications OWNER TO prod_deviantcord;

--
-- Name: deviation_notifications_id_seq; Type: SEQUENCE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE SEQUENCE deviantcord.deviation_notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE deviantcord.deviation_notifications_id_seq OWNER TO prod_deviantcord;

--
-- Name: deviation_notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER SEQUENCE deviantcord.deviation_notifications_id_seq OWNED BY deviantcord.deviation_notifications.id;


--
-- Name: journal_data; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
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
    mature boolean,
    thumb_img_url text,
    last_urls text[],
    last_excerpts text[],
    last_titles text[]
);


ALTER TABLE deviantcord.journal_data OWNER TO prod_deviantcord;

--
-- Name: journal_listeners; Type: TABLE; Schema: deviantcord; Owner: doadmin
--

CREATE TABLE deviantcord.journal_listeners (
    artist text NOT NULL,
    dc_uuid text,
    last_ids text[],
    last_check text,
    latest_update text,
    latest_pp text,
    mature boolean,
    serverid bigint,
    channelid bigint
);


ALTER TABLE deviantcord.journal_listeners OWNER TO doadmin;

--
-- Name: journal_notifications; Type: TABLE; Schema: deviantcord; Owner: doadmin
--

CREATE TABLE deviantcord.journal_notifications (
    channelid bigint NOT NULL,
    artist text,
    pp_url text NOT NULL,
    title text,
    id integer NOT NULL,
    url text,
    thumbnail text,
    notifcation_creation text,
    mature boolean
);


ALTER TABLE deviantcord.journal_notifications OWNER TO doadmin;

--
-- Name: journal_notifications_id_seq; Type: SEQUENCE; Schema: deviantcord; Owner: doadmin
--

CREATE SEQUENCE deviantcord.journal_notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE deviantcord.journal_notifications_id_seq OWNER TO doadmin;

--
-- Name: journal_notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: deviantcord; Owner: doadmin
--

ALTER SEQUENCE deviantcord.journal_notifications_id_seq OWNED BY deviantcord.journal_notifications.id;


--
-- Name: listeners; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
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


ALTER TABLE deviantcord.listeners OWNER TO prod_deviantcord;

--
-- Name: server_config; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE TABLE deviantcord.server_config (
    serverid bigint,
    prefix text,
    errite_optout boolean,
    required_role bigint,
    updated timestamp without time zone DEFAULT now()
);


ALTER TABLE deviantcord.server_config OWNER TO prod_deviantcord;

--
-- Name: status_data; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
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


ALTER TABLE deviantcord.status_data OWNER TO prod_deviantcord;

--
-- Name: test_exp; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE TABLE deviantcord.test_exp (
    column_1 integer
);


ALTER TABLE deviantcord.test_exp OWNER TO prod_deviantcord;

--
-- Name: test_table; Type: TABLE; Schema: deviantcord; Owner: prod_deviantcord
--

CREATE TABLE deviantcord.test_table (
    artist text,
    folder text
);


ALTER TABLE deviantcord.test_table OWNER TO prod_deviantcord;

--
-- Name: deviation_notifications id; Type: DEFAULT; Schema: deviantcord; Owner: prod_deviantcord
--

ALTER TABLE ONLY deviantcord.deviation_notifications ALTER COLUMN id SET DEFAULT nextval('deviantcord.deviation_notifications_id_seq'::regclass);


--
-- Name: journal_notifications id; Type: DEFAULT; Schema: deviantcord; Owner: doadmin
--

ALTER TABLE ONLY deviantcord.journal_notifications ALTER COLUMN id SET DEFAULT nextval('deviantcord.journal_notifications_id_seq'::regclass);


--
-- Data for Name: deviation_notifications; Type: TABLE DATA; Schema: deviantcord; Owner: prod_deviantcord
--

--
-- Data for Name: status_data; Type: TABLE DATA; Schema: deviantcord; Owner: prod_deviantcord
--



--
-- Data for Name: test_exp; Type: TABLE DATA; Schema: deviantcord; Owner: prod_deviantcord
--



--
-- Data for Name: test_table; Type: TABLE DATA; Schema: deviantcord; Owner: prod_deviantcord
--



--
-- Name: deviation_notifications_id_seq; Type: SEQUENCE SET; Schema: deviantcord; Owner: prod_deviantcord
--

SELECT pg_catalog.setval('deviantcord.deviation_notifications_id_seq', 56517, true);


--
-- Name: journal_notifications_id_seq; Type: SEQUENCE SET; Schema: deviantcord; Owner: doadmin
--

SELECT pg_catalog.setval('deviantcord.journal_notifications_id_seq', 1, false);


--
-- Name: TABLE deviant_accounts; Type: ACL; Schema: deviantcord; Owner: doadmin
--

GRANT ALL ON TABLE deviantcord.deviant_accounts TO prod_deviantcord;


--
-- Name: TABLE journal_listeners; Type: ACL; Schema: deviantcord; Owner: doadmin
--

GRANT ALL ON TABLE deviantcord.journal_listeners TO prod_deviantcord;


--
-- Name: TABLE journal_notifications; Type: ACL; Schema: deviantcord; Owner: doadmin
--

GRANT ALL ON TABLE deviantcord.journal_notifications TO prod_deviantcord;


--
-- PostgreSQL database dump complete
--

