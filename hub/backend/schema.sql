--
-- PostgreSQL database dump
--

-- Dumped from database version 16.6 (Ubuntu 16.6-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.6 (Ubuntu 16.6-0ubuntu0.24.04.1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: flaskuser
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO flaskuser;

--
-- Name: plants; Type: TABLE; Schema: public; Owner: flaskuser
--

CREATE TABLE public.plants (
    id integer NOT NULL,
    nickname character varying(255),
    species character varying(255) NOT NULL
);


ALTER TABLE public.plants OWNER TO flaskuser;

--
-- Name: plants_id_seq; Type: SEQUENCE; Schema: public; Owner: flaskuser
--

CREATE SEQUENCE public.plants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.plants_id_seq OWNER TO flaskuser;

--
-- Name: plants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: flaskuser
--

ALTER SEQUENCE public.plants_id_seq OWNED BY public.plants.id;


--
-- Name: plants id; Type: DEFAULT; Schema: public; Owner: flaskuser
--

ALTER TABLE ONLY public.plants ALTER COLUMN id SET DEFAULT nextval('public.plants_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: flaskuser
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: plants plants_nickname_key; Type: CONSTRAINT; Schema: public; Owner: flaskuser
--

ALTER TABLE ONLY public.plants
    ADD CONSTRAINT plants_nickname_key UNIQUE (nickname);


--
-- Name: plants plants_pkey; Type: CONSTRAINT; Schema: public; Owner: flaskuser
--

ALTER TABLE ONLY public.plants
    ADD CONSTRAINT plants_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

