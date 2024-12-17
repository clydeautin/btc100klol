--
-- PostgreSQL database dump
--

-- Dumped from database version 14.13 (Homebrew)
-- Dumped by pg_dump version 14.13 (Homebrew)

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
-- Name: prompttype; Type: TYPE; Schema: public; Owner: clydeautin
--

CREATE TYPE public.prompttype AS ENUM (
    'GET_HOLIDAYS',
    'GENERATE_IMAGE_SAD',
    'GENERATE_IMAGE_HAPPY'
);


ALTER TYPE public.prompttype OWNER TO clydeautin;

--
-- Name: taskstatus; Type: TYPE; Schema: public; Owner: clydeautin
--

CREATE TYPE public.taskstatus AS ENUM (
    'PENDING',
    'PROCESSING',
    'COMPLETED',
    'FAILED'
);


ALTER TYPE public.taskstatus OWNER TO clydeautin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: clydeautin
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO clydeautin;

--
-- Name: image_link; Type: TABLE; Schema: public; Owner: clydeautin
--

CREATE TABLE public.image_link (
    prompt_id integer NOT NULL,
    openai_image_url text NOT NULL,
    s3_image_url text,
    status public.taskstatus DEFAULT 'PENDING'::public.taskstatus NOT NULL,
    id integer NOT NULL,
    created timestamp without time zone NOT NULL,
    created_ts integer NOT NULL,
    last_modified timestamp without time zone NOT NULL,
    last_modified_ts integer NOT NULL
);


ALTER TABLE public.image_link OWNER TO clydeautin;

--
-- Name: image_link_id_seq; Type: SEQUENCE; Schema: public; Owner: clydeautin
--

CREATE SEQUENCE public.image_link_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.image_link_id_seq OWNER TO clydeautin;

--
-- Name: image_link_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: clydeautin
--

ALTER SEQUENCE public.image_link_id_seq OWNED BY public.image_link.id;


--
-- Name: prompt; Type: TABLE; Schema: public; Owner: clydeautin
--

CREATE TABLE public.prompt (
    prompt_text text NOT NULL,
    prompt_date date NOT NULL,
    prompt_type public.prompttype NOT NULL,
    status public.taskstatus DEFAULT 'PENDING'::public.taskstatus NOT NULL,
    id integer NOT NULL,
    created timestamp without time zone NOT NULL,
    created_ts integer NOT NULL,
    last_modified timestamp without time zone NOT NULL,
    last_modified_ts integer NOT NULL
);


ALTER TABLE public.prompt OWNER TO clydeautin;

--
-- Name: prompt_id_seq; Type: SEQUENCE; Schema: public; Owner: clydeautin
--

CREATE SEQUENCE public.prompt_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.prompt_id_seq OWNER TO clydeautin;

--
-- Name: prompt_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: clydeautin
--

ALTER SEQUENCE public.prompt_id_seq OWNED BY public.prompt.id;


--
-- Name: image_link id; Type: DEFAULT; Schema: public; Owner: clydeautin
--

ALTER TABLE ONLY public.image_link ALTER COLUMN id SET DEFAULT nextval('public.image_link_id_seq'::regclass);


--
-- Name: prompt id; Type: DEFAULT; Schema: public; Owner: clydeautin
--

ALTER TABLE ONLY public.prompt ALTER COLUMN id SET DEFAULT nextval('public.prompt_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: clydeautin
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: image_link image_link_pkey; Type: CONSTRAINT; Schema: public; Owner: clydeautin
--

ALTER TABLE ONLY public.image_link
    ADD CONSTRAINT image_link_pkey PRIMARY KEY (id);


--
-- Name: prompt prompt_pkey; Type: CONSTRAINT; Schema: public; Owner: clydeautin
--

ALTER TABLE ONLY public.prompt
    ADD CONSTRAINT prompt_pkey PRIMARY KEY (id);


--
-- Name: ix_image_link_prompt_id; Type: INDEX; Schema: public; Owner: clydeautin
--

CREATE INDEX ix_image_link_prompt_id ON public.image_link USING btree (prompt_id);


--
-- Name: image_link image_link_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: clydeautin
--

ALTER TABLE ONLY public.image_link
    ADD CONSTRAINT image_link_prompt_id_fkey FOREIGN KEY (prompt_id) REFERENCES public.prompt(id);


--
-- PostgreSQL database dump complete
--

