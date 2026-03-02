package oauth

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
)

type WeChatProvider struct {
	appID       string
	appSecret   string
	redirectURL string
}

func NewWeChatProvider(appID, appSecret, redirectURL string) *WeChatProvider {
	return &WeChatProvider{
		appID:       appID,
		appSecret:   appSecret,
		redirectURL: redirectURL,
	}
}

func (p *WeChatProvider) GetAuthURL(state string) string {
	params := url.Values{
		"appid":         {p.appID},
		"redirect_uri":  {p.redirectURL},
		"response_type": {"code"},
		"scope":         {"snsapi_login"},
		"state":         {state},
	}
	return "https://open.weixin.qq.com/connect/qrconnect?" + params.Encode() + "#wechat_redirect"
}

type WeChatAccessTokenResponse struct {
	AccessToken  string `json:"access_token"`
	ExpiresIn    int    `json:"expires_in"`
	RefreshToken string `json:"refresh_token"`
	OpenID       string `json:"openid"`
	UnionID      string `json:"unionid"`
	ErrCode      int    `json:"errcode"`
	ErrMsg       string `json:"errmsg"`
}

func (p *WeChatProvider) GetAccessToken(code string) (*WeChatAccessTokenResponse, error) {
	params := url.Values{
		"appid":      {p.appID},
		"secret":     {p.appSecret},
		"code":       {code},
		"grant_type": {"authorization_code"},
	}

	resp, err := http.Get("https://api.weixin.qq.com/sns/oauth2/access_token?" + params.Encode())
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var result WeChatAccessTokenResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, err
	}

	if result.ErrCode != 0 {
		return nil, fmt.Errorf("wechat api error: %d - %s", result.ErrCode, result.ErrMsg)
	}

	return &result, nil
}

type WeChatUserInfo struct {
	OpenID     string   `json:"openid"`
	UnionID    string   `json:"unionid"`
	Nickname   string   `json:"nickname"`
	Sex        int      `json:"sex"`
	Province   string   `json:"province"`
	City       string   `json:"city"`
	Country    string   `json:"country"`
	HeadImgURL string   `json:"headimgurl"`
	Privilege  []string `json:"privilege"`
	ErrCode    int      `json:"errcode"`
	ErrMsg     string   `json:"errmsg"`
}

func (p *WeChatProvider) GetUserInfo(accessToken, openID string) (*WeChatUserInfo, error) {
	params := url.Values{
		"access_token": {accessToken},
		"openid":       {openID},
	}

	resp, err := http.Get("https://api.weixin.qq.com/sns/userinfo?" + params.Encode())
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var result WeChatUserInfo
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, err
	}

	if result.ErrCode != 0 {
		return nil, fmt.Errorf("wechat api error: %d - %s", result.ErrCode, result.ErrMsg)
	}

	return &result, nil
}

func (p *WeChatProvider) RefreshAccessToken(refreshToken string) (*WeChatAccessTokenResponse, error) {
	params := url.Values{
		"appid":         {p.appID},
		"grant_type":    {"refresh_token"},
		"refresh_token": {refreshToken},
	}

	resp, err := http.Get("https://api.weixin.qq.com/sns/oauth2/refresh_token?" + params.Encode())
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var result WeChatAccessTokenResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, err
	}

	if result.ErrCode != 0 {
		return nil, fmt.Errorf("wechat api error: %d - %s", result.ErrCode, result.ErrMsg)
	}

	return &result, nil
}

type QQProvider struct {
	appID       string
	appKey      string
	redirectURL string
}

func NewQQProvider(appID, appKey, redirectURL string) *QQProvider {
	return &QQProvider{
		appID:       appID,
		appKey:      appKey,
		redirectURL: redirectURL,
	}
}

func (p *QQProvider) GetAuthURL(state string) string {
	params := url.Values{
		"response_type": {"code"},
		"client_id":     {p.appID},
		"redirect_uri":  {p.redirectURL},
		"state":         {state},
		"scope":         {"get_user_info"},
	}
	return "https://graph.qq.com/oauth2.0/authorize?" + params.Encode()
}

type QQAccessTokenResponse struct {
	AccessToken  string `json:"access_token"`
	ExpiresIn    int    `json:"expires_in"`
	RefreshToken string `json:"refresh_token"`
}

func (p *QQProvider) GetAccessToken(code string) (*QQAccessTokenResponse, error) {
	params := url.Values{
		"grant_type":   {"authorization_code"},
		"client_id":    {p.appID},
		"client_secret": {p.appKey},
		"code":         {code},
		"redirect_uri": {p.redirectURL},
	}

	resp, err := http.Get("https://graph.qq.com/oauth2.0/token?" + params.Encode())
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	values, err := url.ParseQuery(string(body))
	if err != nil {
		return nil, err
	}

	if values.Get("error") != "" {
		return nil, fmt.Errorf("qq api error: %s - %s", values.Get("error"), values.Get("error_description"))
	}

	return &QQAccessTokenResponse{
		AccessToken:  values.Get("access_token"),
		ExpiresIn:    parseInt(values.Get("expires_in")),
		RefreshToken: values.Get("refresh_token"),
	}, nil
}

type QQOpenIDResponse struct {
	ClientID string `json:"client_id"`
	OpenID   string `json:"openid"`
	Error    string `json:"error"`
}

func (p *QQProvider) GetOpenID(accessToken string) (string, error) {
	params := url.Values{
		"access_token": {accessToken},
	}

	resp, err := http.Get("https://graph.qq.com/oauth2.0/me?" + params.Encode())
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	bodyStr := string(body)
	if strings.Contains(bodyStr, "error") {
		return "", errors.New("qq api error: " + bodyStr)
	}

	jsonStr := strings.TrimPrefix(strings.TrimSuffix(bodyStr, ");"), "callback(")
	var result QQOpenIDResponse
	if err := json.Unmarshal([]byte(jsonStr), &result); err != nil {
		return "", err
	}

	if result.Error != "" {
		return "", errors.New(result.Error)
	}

	return result.OpenID, nil
}

type QQUserInfo struct {
	Ret          int    `json:"ret"`
	Msg          string `json:"msg"`
	Nickname     string `json:"nickname"`
	FigureURL    string `json:"figureurl"`
	FigureURLQQ1 string `json:"figureurl_qq_1"`
	FigureURLQQ2 string `json:"figureurl_qq_2"`
	Gender       string `json:"gender"`
}

func (p *QQProvider) GetUserInfo(accessToken, openID string) (*QQUserInfo, error) {
	params := url.Values{
		"access_token":       {accessToken},
		"oauth_consumer_key": {p.appID},
		"openid":             {openID},
	}

	resp, err := http.Get("https://graph.qq.com/user/get_user_info?" + params.Encode())
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var result QQUserInfo
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, err
	}

	if result.Ret != 0 {
		return nil, fmt.Errorf("qq api error: %d - %s", result.Ret, result.Msg)
	}

	return &result, nil
}

func parseInt(s string) int {
	var result int
	fmt.Sscanf(s, "%d", &result)
	return result
}

type OAuthProvider interface {
	GetAuthURL(state string) string
}

type OAuthService struct {
	wechatProvider *WeChatProvider
	qqProvider     *QQProvider
}

func NewOAuthService(wechatAppID, wechatAppSecret, wechatRedirectURL, qqAppID, qqAppKey, qqRedirectURL string) *OAuthService {
	return &OAuthService{
		wechatProvider: NewWeChatProvider(wechatAppID, wechatAppSecret, wechatRedirectURL),
		qqProvider:     NewQQProvider(qqAppID, qqAppKey, qqRedirectURL),
	}
}

func (s *OAuthService) GetWeChatProvider() *WeChatProvider {
	return s.wechatProvider
}

func (s *OAuthService) GetQQProvider() *QQProvider {
	return s.qqProvider
}

func (s *OAuthService) GetAuthURL(provider, state string) string {
	switch provider {
	case "wechat":
		return s.wechatProvider.GetAuthURL(state)
	case "qq":
		return s.qqProvider.GetAuthURL(state)
	default:
		return ""
	}
}

type OAuthUserInfo struct {
	Provider   string
	ProviderID string
	Nickname   string
	Avatar     string
	Email      string
}

func (s *OAuthService) HandleWeChatCallback(ctx context.Context, code string) (*OAuthUserInfo, *WeChatAccessTokenResponse, error) {
	tokenResp, err := s.wechatProvider.GetAccessToken(code)
	if err != nil {
		return nil, nil, err
	}

	userInfo, err := s.wechatProvider.GetUserInfo(tokenResp.AccessToken, tokenResp.OpenID)
	if err != nil {
		return nil, nil, err
	}

	providerID := tokenResp.UnionID
	if providerID == "" {
		providerID = tokenResp.OpenID
	}

	return &OAuthUserInfo{
		Provider:   "wechat",
		ProviderID: providerID,
		Nickname:   userInfo.Nickname,
		Avatar:     userInfo.HeadImgURL,
	}, tokenResp, nil
}

func (s *OAuthService) HandleQQCallback(ctx context.Context, code string) (*OAuthUserInfo, *QQAccessTokenResponse, error) {
	tokenResp, err := s.qqProvider.GetAccessToken(code)
	if err != nil {
		return nil, nil, err
	}

	openID, err := s.qqProvider.GetOpenID(tokenResp.AccessToken)
	if err != nil {
		return nil, nil, err
	}

	userInfo, err := s.qqProvider.GetUserInfo(tokenResp.AccessToken, openID)
	if err != nil {
		return nil, nil, err
	}

	avatar := userInfo.FigureURLQQ2
	if avatar == "" {
		avatar = userInfo.FigureURLQQ1
	}
	if avatar == "" {
		avatar = userInfo.FigureURL
	}

	return &OAuthUserInfo{
		Provider:   "qq",
		ProviderID: openID,
		Nickname:   userInfo.Nickname,
		Avatar:     avatar,
	}, tokenResp, nil
}
