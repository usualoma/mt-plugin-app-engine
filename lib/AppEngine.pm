# Copyright (c) 2010 ToI Inc. All rights reserved.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

package AppEngine;

use strict;
use warnings;

use LWP::UserAgent;

sub plugin {
	MT->component('AppEngine');
}

sub endpoint {
	my ($scope) = @_;
	&plugin->get_config_value('app_engine_endpoint', $scope);
}

sub build_file {
	my ($cb, %params) = @_;

	my $scope    = 'blog:' . $params{'Blog'}->id;
	my $endpoint = &endpoint($scope); 

	$endpoint or return 1;

	my $url = $params{'FileInfo'}->url;
	$url =~ s{\Ahttp://[^/]*}{};
	$url =~ s{\A/*}{};


	my $ua = LWP::UserAgent->new;
	if (my $proxy = MT->config('HTTPProxy')) {
		$ua->proxy('http', $proxy);
	}
	$ua->timeout(10);

	my $response = $ua->post($endpoint, {
		'url'     => $url,
		'content' => ${ $params{'content'} },
	});

	if ($response->is_success) {
		# OK
	}
	else {
		MT->log($response->status_line . ':' . $response->content);
		die $response->status_line;
	}

	1;
}

1;
