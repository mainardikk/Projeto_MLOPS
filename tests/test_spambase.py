"""Preparação do novo domínio: sem rede e sem substituir o pipeline original."""

import json
import shutil
from itertools import combinations

import numpy as np
import pandas as pd
import pytest

from mlops_demo import spambase


@pytest.fixture(scope="module")
def original_spambase():
    return spambase.carregar_original()


@pytest.mark.dados
def test_fonte_uci_integra_tem_4601_linhas_57_atributos_e_alvo_binario(original_spambase):
    assert original_spambase.shape == (4601, 58)
    assert len(spambase.FEATURES_SPAMBASE) == 57
    assert original_spambase["spam"].value_counts().to_dict() == {0: 2788, 1: 1813}
    assert not original_spambase.isna().any().any()
    assert spambase.FEATURES_SPAMBASE[51] == "char_freq_exclamation"
    assert spambase.FEATURES_SPAMBASE[52] == "char_freq_dollar"


@pytest.mark.dados
def test_artefatos_versionados_sao_reproduzidos_byte_a_byte_sem_rede(monkeypatch):
    def proibir_rede(*args, **kwargs):
        pytest.fail("A reprodução dos dados versionados não pode depender da UCI.")

    monkeypatch.setattr(spambase, "urlopen", proibir_rede)
    spambase.verificar()


@pytest.mark.dados
def test_particoes_publicadas_cobrem_base_limpa_sem_vazamento(original_spambase):
    limpo, _ = spambase.limpar_duplicatas(original_spambase)
    preparados = spambase.PASTA_SPAMBASE / "preparado"
    chaves = {}
    for nome, arquivo in spambase.ARQUIVOS_PARTICOES.items():
        df = pd.read_csv(preparados / arquivo)
        spambase.validar_spambase(df)
        chaves[nome] = set(map(tuple, df[spambase.FEATURES_SPAMBASE].to_numpy()))
        assert len(chaves[nome]) == len(df)
        assert set(df["spam"]) == {0, 1}
        assert abs(df["spam"].mean() - limpo["spam"].mean()) < 0.002
    assert {nome: len(valores) for nome, valores in chaves.items()} == {
        "treino": 2522,
        "holdout": 841,
        "reserva": 841,
    }
    for a, b in combinations(chaves, 2):
        assert chaves[a].isdisjoint(chaves[b]), f"Vazamento entre {a} e {b}."
    assert set.union(*chaves.values()) == set(
        map(tuple, limpo[spambase.FEATURES_SPAMBASE].to_numpy())
    )


@pytest.mark.dados
def test_analise_registra_duplicatas_e_conflitos_reais(original_spambase):
    limpo, analise = spambase.limpar_duplicatas(original_spambase)
    assert analise["duplicatas_completas_excedentes"] == 391
    assert analise["duplicatas_atributos_excedentes"] == 394
    assert analise["grupos_com_rotulos_conflitantes"] == 3
    assert analise["linhas_conflitantes_excluidas"] == 6
    assert analise["linhas_duplicadas_excluidas_apos_conflitos"] == 391
    assert len(limpo) == 4204
    assert not limpo.duplicated(subset=spambase.FEATURES_SPAMBASE).any()
    manifesto = json.loads(
        (spambase.PASTA_SPAMBASE / "preparado" / "manifesto.json").read_text(encoding="utf-8")
    )
    assert manifesto["analise_duplicatas"] == analise


@pytest.mark.codigo
def test_limpeza_exclui_ambos_os_rotulos_conflitantes_sem_votar_na_maioria(original_spambase):
    base = original_spambase.iloc[:3].copy().reset_index(drop=True)
    base["spam"] = [0, 0, 1]
    conflitante = base.iloc[[0]].copy()
    conflitante["spam"] = 1
    entrada = pd.concat([base, conflitante, base.iloc[[0, 1]]], ignore_index=True)
    antes = entrada.copy()
    limpo, _ = spambase.limpar_duplicatas(entrada)
    pd.testing.assert_frame_equal(limpo, base.iloc[1:].reset_index(drop=True))
    pd.testing.assert_frame_equal(entrada, antes)


@pytest.mark.codigo
def test_divisao_rejeita_duplicatas_antes_de_sortear(original_spambase):
    with pytest.raises(ValueError, match="Remova duplicatas"):
        spambase.dividir_spambase(original_spambase)


@pytest.mark.codigo
def test_fonte_corrompida_e_rejeitada_antes_da_preparacao(tmp_path):
    shutil.copytree(spambase.PASTA_SPAMBASE / "original", tmp_path / "original")
    fonte = tmp_path / "original" / "spambase.data"
    fonte.write_bytes(fonte.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="SHA-256 divergente"):
        spambase.preparar(tmp_path)
    assert not (tmp_path / "preparado").exists()


@pytest.mark.codigo
def test_verificacao_detecta_particao_adulterada_sem_corrigi_la(tmp_path):
    shutil.copytree(spambase.PASTA_SPAMBASE / "original", tmp_path / "original")
    shutil.copytree(spambase.PASTA_SPAMBASE / "preparado", tmp_path / "preparado")
    reserva = tmp_path / "preparado" / "base_reserva.csv"
    adulterado = reserva.read_bytes() + b"\n"
    reserva.write_bytes(adulterado)
    with pytest.raises(ValueError, match="base_reserva.csv"):
        spambase.verificar(tmp_path)
    assert reserva.read_bytes() == adulterado


@pytest.mark.dados
@pytest.mark.parametrize(
    ("coluna", "valor", "mensagem"),
    [
        ("word_freq_free", 100.1, "entre 0 e 100"),
        ("char_freq_dollar", -0.1, "entre 0 e 100"),
        ("word_freq_money", np.nan, "nulos ou não finitos"),
        ("word_freq_money", np.inf, "nulos ou não finitos"),
        ("spam", 2, "alvo spam"),
        ("capital_run_length_average", 0, "pelo menos 1"),
        ("capital_run_length_longest", 1.5, "inteiros"),
        ("capital_run_length_total", 1, "média <= maior sequência <= total"),
    ],
)
def test_validador_spambase_rejeita_valores_impossiveis(original_spambase, coluna, valor, mensagem):
    invalido = original_spambase.iloc[:2].copy()
    invalido[coluna] = invalido[coluna].astype(float)
    invalido.loc[invalido.index[0], coluna] = valor
    with pytest.raises(ValueError, match=mensagem):
        spambase.validar_spambase(invalido)


@pytest.mark.dados
def test_validador_spambase_rejeita_texto_booleano_e_esquema_incompleto(original_spambase):
    for valor in ("1.5", True):
        invalido = original_spambase.iloc[:2].copy()
        invalido["word_freq_free"] = valor
        with pytest.raises(ValueError, match="tipo numérico"):
            spambase.validar_spambase(invalido)
    with pytest.raises(ValueError, match="Esquema Spambase inválido"):
        spambase.validar_spambase(original_spambase.drop(columns=["char_freq_dollar"]))
