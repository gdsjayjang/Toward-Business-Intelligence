import pandas as pd

CLUB_STATUS_COLORS = {
    'ACTIVE':       'green',
    'PRE-CREATE':   'blue',
    'LEFT CLUB':    'red'}

NEW_FREQUENCY_LABELS = {
    'Regularly':    '정기 수신',
    'Monthly':      '월간 수신',
    'NONE':         '미수신',}

NEWS_FREQUENCY_COLORS = {
    '정기 수신':    'green',
    '월간 수신':    'blue',
    '미수신':       'red',
    '정보 없음':    'grey',}

SEGMENT_COLORS = {
    'VIP':          'violet',
    '충성':         'green',
    '신규':         'blue',
    '이탈위험':     'red',
    '일반':         'grey',}


def club_status_badge(value):
    '''클럽 멤버 상태 -> 색상 매핑'''
    if pd.isna(value): return ':grey[**정보 없음**]'
    color = CLUB_STATUS_COLORS.get(value, 'grey')
    return f":{color}[**{value}**]"

def news_frequency_label(value):
    if pd.isna(value): return '정보 없음'
    return NEW_FREQUENCY_LABELS.get(value, value)

def news_frequency_badge(value):
    '''뉴스 수신 값 -> 한국어 레이블 + 색상 매핑'''
    label = news_frequency_label(value)
    color = NEWS_FREQUENCY_COLORS.get(label, "grey")
    return f":{color}[**{label}**]"

def segment_badge(value):
    '''세그먼트 -> 색상 매핑'''
    if pd.isna(value): return ':grey[**미분류**]'
    color = SEGMENT_COLORS.get(value, 'gery')
    return f":{color}[**{value}**]"