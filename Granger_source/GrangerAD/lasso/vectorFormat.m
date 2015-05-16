function out = vectorFormat(type, pars)
N = pars.N;
L = pars.L;
out = cell(1, 3);
if type == '0'
    % Alpha
    out{1} = cell(1, N);
    for i = 1:N
        out{1}{i} = zeros(size(pars.graph{i}.neighbs));
    end
    % Beta
    out{2} = zeros(N, L);
    % C
    out{3} = zeros(1, N);
elseif type == '1'
    % Alpha
    out{1} = cell(1, N);
    for i = 1:N
        out{1}{i} = pars.lamA*ones(size(pars.graph{i}.neighbs));
    end
    % Beta
    out{2} = pars.lamB*ones(N, L);
    % Nu
    out{3} = 0*ones(1, N);
else
    % Alpha
    out{1} = cell(1, N);
    for i = 1:N
        out{1}{i} = rand(size(pars.graph{i}.neighbs));
    end
    % Beta
    out{2} = rand(N, L);
    % C
    out{3} = rand(1, N);
end
end