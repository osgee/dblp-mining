import pymysql
import numpy as np
import operator


type_dblp = 1
type_sim = 2


# drop view journal_sample;
# drop view article_sample;
# drop view author_article_sample;
# drop view author_sample;

# create view journal_sample as select j.journalid, j.journal from journal j where j.journalid=12539 or j.journalid=14369 or j.journalid=175 or j.journalid=33069 or j.journalid=14352 or j.journalid=18733;
#
# create view article_sample as select a.articleid, a.title, a.`year`, a.journalid from article a where a.journalid in (select js.journalid from journal_sample js);
# create view author_article_sample as select * from author_article aa where aa.articleid in (select arsample.articleid from article_sample arsample);
# create view author_sample as select * from author a where a.authorid in (select distinct(aasample.authorid) from author_article_sample aasample);

def pick_journal(conn, journal):
    cur = conn.cursor()
    try:
        cur.execute('drop view journal_sample;')
    except pymysql.err.IntegrityError as e:
        pass
    except pymysql.err.InternalError as e:
        pass

    try:
        cur.execute('drop view article_sample;')
    except pymysql.err.IntegrityError as e:
        pass
    except pymysql.err.InternalError as e:
        pass

    try:
        cur.execute('drop view author_article_sample;')
    except pymysql.err.IntegrityError as e:
        pass
    except pymysql.err.InternalError as e:
        pass
    try:
        cur.execute('drop view author_sample;')
    except pymysql.err.IntegrityError as e:
        pass
    except pymysql.err.InternalError as e:
        pass

    sql1 = 'create view journal_sample as select j.journalid, j.journal from journal j where '
    # j.journalid = 12539 or j.journalid = 14369 or j.journalid = 175 or j.journalid = 33069 or j.journalid = 14352 or j.journalid = 18733

    for i in range(len(journal)):
        sql1 += 'j.journalid = %s ' % journal[i]
        if i < len(journal)-1:
            sql1 += 'or '
        else:
            sql1 += ';'
    sql2 = 'create view article_sample as select a.articleid, a.title, a.`year`, a.journalid from article a where a.journalid in (select js.journalid from journal_sample js);'
    sql3 = 'create view author_article_sample as select * from author_article aa where aa.articleid in (select arsample.articleid from article_sample arsample);'
    sql4 = 'create view author_sample as select * from author a where a.authorid in (select distinct(aasample.authorid) from author_article_sample aasample);'
    print(sql1)
    print(sql2)
    print(sql3)
    print(sql4)
    cur.execute(sql1)
    cur.execute(sql2)
    cur.execute(sql3)
    cur.execute(sql4)


def get_data(type, cached = False, journal=[], **keywords):
    if type == type_dblp:
        if not cached:
            conn = pymysql.connect(host='localhost',port=3306,user='user',password='password',db='dblp')
            if len(journal) > 0:
                pick_journal(conn, journal)

            cur = conn.cursor()

            cur.execute('select count(*) from article_sample where 1=1;')

            article_size = cur.fetchone()[0]

            cur.execute('select count(*) from journal_sample where 1=1;')

            journal_size = cur.fetchone()[0]

            cur.execute('select count(*) from author_sample where 1=1;')

            author_size = cur.fetchone()[0]

            cur.execute('select articleId, journalId from article_sample where 1=1;')

            d_Y = {}
            d_Z = {}

            A_ZY = [([0.0]*article_size) for i in range(journal_size)]

            count_y = 0
            count_z = 0

            for c in cur.fetchall():
                if c[1] in d_Z.keys():
                    d_Y[c[0]] = count_y
                    A_ZY[count_z-1][count_y] = 1
                else:
                    d_Z[c[1]] = count_z
                    d_Y[c[0]] = count_y
                    A_ZY[count_z][count_y] = 1
                    count_z += 1
                count_y += 1

            print("ZY ok")

            cur.execute('select articleId, authorId from author_article_sample where 1=1;')

            d_X = {}
            A_XY = [([0.0]*article_size) for i in range(author_size)]

            count_x = 0

            for c in cur.fetchall():
                if c[1] in d_X.keys():
                    A_XY[d_X[c[1]]][d_Y[c[0]]] = 1
                else:
                    d_X[c[1]] = count_x
                    A_XY[count_x][d_Y[c[0]]] = 1
                    count_x += 1

            print("XY ok")

            W_ZY = np.array(A_ZY)
            W_XY = np.array(A_XY)
            # W_XX_T = np.dot(W_XY, np.transpose(W_XY))
            # W_XX = W_XX_T
            W_XX = np.zeros([author_size, author_size])
            print("XX ok")


            W_YY = np.zeros([article_size, article_size])
            print("YY ok")

            if 'refer' in keywords.keys() and not keywords['refer']:
                W_YY = np.zeros([article_size, article_size])

            if 'cache' in keywords.keys() and keywords['cache']:
                np.save('W_XX.npy',W_XX)
                np.save('W_XY.npy', W_XY)
                np.save('W_ZY.npy', W_ZY)
                np.save('W_YY.npy', W_YY)
                np.save('d_X.npy', d_X)
                np.save('d_Y.npy', d_Y)
                np.save('d_Z.npy', d_Z)

            return W_XX, W_XY, W_ZY, W_YY, d_X, d_Y, d_Z
        else:
            W_XX = np.load('W_XX.npy')
            W_XY = np.load('W_XY.npy')
            W_ZY = np.load('W_ZY.npy')
            W_YY = np.load('W_YY.npy')
            d_X = np.load('d_X.npy')
            d_Y = np.load('d_Y.npy')
            d_Z = np.load('d_Z.npy')

            if 'refer' in keywords.keys() and not keywords['refer']:
                W_YY = np.zeros([article_size, article_size])


            return W_XX, W_XY, W_ZY, W_YY, d_X, d_Y, d_Z

    elif type == type_sim:

        conn = pymysql.connect(host='localhost', port=3306, user='user', password='password', db='sim')
        cur = conn.cursor()

        cur.execute('select count(*) from article;')

        article_size = cur.fetchone()[0]

        cur.execute('select count(*) from journal;')

        journal_size = cur.fetchone()[0]

        cur.execute('select count(*) from author;')

        author_size = cur.fetchone()[0]

        cur.execute('select articleId, journalId from article;')

        d_Y = {}
        d_Z = {}

        A_ZY = [([0.0] * article_size) for i in range(journal_size)]

        count_y = 0
        count_z = 0

        for c in cur.fetchall():
            if c[1] in d_Z.keys():
                d_Y[c[0]] = count_y
                A_ZY[count_z - 1][count_y] = 1
            else:
                d_Z[c[1]] = count_z
                d_Y[c[0]] = count_y
                A_ZY[count_z][count_y] = 1
                count_z += 1
            count_y += 1

        print("ZY ok")

        cur.execute('select articleId, authorId from author_article;')

        d_X = {}
        A_XY = [([0.0] * article_size) for i in range(author_size)]

        count_x = 0

        for c in cur.fetchall():
            if c[1] in d_X.keys():
                A_XY[d_X[c[1]]][d_Y[c[0]]] = 1
            else:
                d_X[c[1]] = count_x
                A_XY[count_x][d_Y[c[0]]] = 1
                count_x += 1

        print("XY ok")

        cur.execute('select articlereferred, articlereferring from article_article;')

        A_YY = [([0.0] * article_size) for i in range(article_size)]

        count_x = 0

        for c in cur.fetchall():
            if c[0] in d_Y.keys() and c[1] in d_Y.keys():
                A_YY[d_Y[c[0]]][d_Y[c[1]]] = 1


        print("YY ok")

        W_ZY = np.array(A_ZY)
        W_XY = np.array(A_XY)

        W_XX_T = np.dot(W_XY, np.transpose(W_XY))
        print("XX ok")

        W_XX = W_XX_T
        W_YY = np.array(A_YY)

        # W_XX = np.array([[2, 1, 1, 0],
        #                  [1, 2, 0, 1],
        #                  [1, 0, 1, 0],
        #                  [0, 1, 0, 1]])
        #
        # W_XY = np.array([[1, 1, 0],
        #                  [1, 0, 1],
        #                  [0, 1, 0],
        #                  [0, 0, 1]])
        #
        # W_ZY = np.array([[1, 1, 0],
        #                  [0, 0, 1]])
        #
        # W_YY = np.array([[0, 0, 0],
        #                  [0, 0, 1],
        #                  [0, 0, 0]])

        if 'refer' in keywords.keys() and not keywords['refer']:
            W_YY = np.zeros([article_size, article_size])

        return W_XX, W_XY, W_ZY, W_YY,d_X, d_Y, d_Z


def to_csv(W_XX, W_XY, W_ZY, W_YY,d_X, d_Y, d_Z):
    d_nodes = {}
    with open('nodes.csv', 'w+') as nodes:
        nodes.write('Id,Label,Modularity Class\n')
        index = 0
        for z in d_Z.keys():
            label = 'journal'+str(d_Z[z]+1)
            d_nodes[label] = index
            index +=1
            nodes.write(str(index)+','+label+','+str(1)+'\n')
        for y in d_Y.keys():
            label = 'article'+str(d_Y[y]+1)
            d_nodes[label] = index
            index += 1
            nodes.write(str(index) + ',' + label + ',' + str(2) + '\n')
        for x in d_X.keys():
            label = 'author' + str(d_X[x]+1)
            d_nodes[label] = index
            index += 1
            nodes.write(str(index) + ',' + label + ',' + str(3) + '\n')
    X_S = W_XY.shape[0]  # author size
    Y_S = W_XY.shape[1]  # article size
    Z_S = W_ZY.shape[0]  # journal size
    with open('edges.csv','w+') as edges:
        edges.write('Source,Target,Type,Id,Label,Weight\n')
        index2 = 1
        for r in range(Z_S):
            for c in range(Y_S):
                if W_ZY[r, c] == 1:
                    edges.write(str(r+1)+','+str(c+Z_S+1)+','+'Undirected'+','+str(index2)+','+str(index2)+','+'1\n')
                    index2 +=1
        W_YX = np.transpose(W_XY)
        for r in range(Y_S):
            for c in range(X_S):
                if W_YX[r, c] == 1:
                    edges.write(str(r+Z_S+1) + ',' + str(c+Z_S+Y_S+1) + ',' + 'Undirected' + ',' + str(index2) + ',' + str(
                        index2) + ',' + '1\n')
                    index2 += 1
        for r in range(Y_S):
            for c in range(Y_S):
                if W_YY[r, c] == 1:
                    edges.write(
                        str(r + Z_S+1) + ',' + str(c + Z_S+1) + ',' + 'Directed' + ',' + str(index2) + ',' + str(
                            index2) + ',' + '1\n')
                    index2 += 1
        # for r in range(X_S):
        #     for c in range(X_S):
        #         if W_XX[r, c] != 0:
        #             edges.write(
        #                 str(r + Z_S + Y_S + 1) + ',' + str(c + Z_S + Y_S + 1) + ',' + 'Undirected' + ',' + str(index2) + ',' + str(
        #                     index2) + ',' + str(W_XX[r, c]) + '\n')
        #             index2 += 1


def init_array(size):
    return np.array([1/size for i in range(size)])


def normalize(array):
    return array/array.sum()


def handle_out(matrix):
    return matrix/matrix.sum(axis=1)[:, None]


def handle_xx(matrix):
    return handle_out(matrix)


def handle_xy(matrix):
    return handle_out(matrix)


def handle_zy(matrix):
    return handle_out(matrix)


def handle_yz(matrix):
    return handle_out(matrix)


def is_stable(old,new):
    return abs((old[0]-new[0])/old[0]) < 0.001


def sort_print(R, d):
    x = {}
    for i in d.keys():
        x[i] = R[d[i]]
    sorted_x = sorted(x.items(), key=operator.itemgetter(1), reverse=True)
    print(sorted_x)


# W_XX, W_XY, W_ZY, W_YY, d_X, d_Y, d_Z = get_data(type_dblp, False, [22328, 34188, 40186, 7094, 3775, 2435, 19041, 22813, 33069, 12539], cache=False)
# W_XX, W_XY, W_ZY, W_YY, d_X, d_Y, d_Z = get_data(type_dblp, False, [40218, 14225, 40192, 20596, 1394])
W_XX, W_XY, W_ZY, W_YY, d_X, d_Y, d_Z = get_data(type_sim, refer=True)
to_csv(W_XX, W_XY, W_ZY, W_YY,d_X, d_Y, d_Z)


print(W_XX)
print(W_XX.shape)
print(W_XY)
print(W_XY.shape)
print(W_ZY)
print(W_ZY.shape)
print(W_YY)
print(W_YY.shape)

X_S = W_XY.shape[0]  # author size
Y_S = W_XY.shape[1]  # article size
Z_S = W_ZY.shape[0]  # journal size

R_X = init_array(X_S)
R_Y = init_array(Y_S)
R_Z = init_array(Z_S)


W_XX = handle_xx(W_XX)
W_XY = handle_xy(W_XY)
W_ZY = handle_zy(W_ZY)


W_YX = np.transpose(W_XY)
W_YZ = np.transpose(W_ZY)
W_YZ = handle_yz(W_YZ)

d = 0.85

R_Z_O = R_Z

for i in range(100):
    print("iteration-"+str(i))
    R_X = np.dot(W_XX, R_X) + np.dot(W_XY, R_Y)
    R_X = normalize(R_X)

    R_Y = np.dot(W_YX, R_X)+np.dot(W_YZ, R_Z)+(1-d)/Y_S+d*np.dot(W_YY, R_Y)
    # R_Y = np.dot(W_YX, R_X) + np.dot(W_YZ, R_Z)
    R_Y = normalize(R_Y)

    R_Z = np.dot(W_ZY, R_Y)
    R_Z = normalize(R_Z)
    if i>10 and is_stable(R_Z_O, R_Z):
        break
    else:
        R_Z_O = R_Z


# print(R_X)
# print(d_X)
# print(R_Y)
# print(d_Y)
# print(R_Z)
# print(d_Z)
sort_print(R_X, d_X)
sort_print(R_Y, d_Y)
sort_print(R_Z, d_Z)
# print(d_Z)



